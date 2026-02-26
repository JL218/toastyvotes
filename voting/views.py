from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Count
from django.db import transaction
from .models import VoteSession, Role, Vote, AdminProfile
from .forms import UserRegistrationForm, VoteSessionForm, VoteForm
import json


def home(request):
    """Home view showing welcome message and instructions"""
    return render(request, 'voting/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created! You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'voting/register.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard view for users"""
    # Check if the user is a platform admin
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    
    # Get the latest active voting session (not expired, polls not closed)
    now = timezone.now()
    latest_active_session = VoteSession.objects.filter(
        is_active=True,
        polls_closed=False,
        expires_at__gt=now
    ).order_by('-created_at').first()
    
    if is_admin:
        # For admins, show their created vote sessions
        vote_sessions = VoteSession.objects.filter(created_by=request.user)
    else:
        # For regular users, show their votes
        user_votes = Vote.objects.filter(user=request.user)
        vote_sessions = VoteSession.objects.filter(votes__in=user_votes).distinct()
    
    # Check if user has already voted in the active session
    has_voted_in_active = False
    if latest_active_session:
        has_voted_in_active = Vote.objects.filter(
            user=request.user, 
            vote_session=latest_active_session
        ).exists()
    
    context = {
        'vote_sessions': vote_sessions,
        'is_admin': is_admin,
        'latest_active_session': latest_active_session,
        'has_voted_in_active': has_voted_in_active
    }
    return render(request, 'voting/dashboard.html', context)


@login_required
def create_vote_session(request):
    """View for creating a new vote session (admin only)"""
    # Check if the user is a platform admin
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not is_admin:
        return HttpResponseForbidden("You must be an admin to create vote sessions.")
    
    # Category definitions for the form
    categories = [
        {'key': 'SPEAKER', 'label': 'Prepared Speakers'},
        {'key': 'EVALUATOR', 'label': 'Evaluators'},
        {'key': 'TABLE_TOPICS', 'label': 'Table Topics Speakers'},
    ]
    
    if request.method == 'POST':
        session_form = VoteSessionForm(request.POST)
        
        if session_form.is_valid():
            # Collect participant names from POST data
            role_data = []  # list of (role_type, position, name)
            for cat in categories:
                names = request.POST.getlist(f"participant_{cat['key']}")
                for pos, name in enumerate(names, start=1):
                    name = name.strip()
                    if name:
                        role_data.append((cat['key'], pos, name))
            
            if not role_data:
                messages.error(request, 'Please add at least one participant.')
            else:
                with transaction.atomic():
                    vote_session = session_form.save(commit=False)
                    vote_session.created_by = request.user
                    vote_session.expires_at = timezone.now() + timezone.timedelta(hours=24)
                    vote_session.save()
                    
                    for role_type, position, name in role_data:
                        Role.objects.create(
                            vote_session=vote_session,
                            role_type=role_type,
                            position=position,
                            name=name,
                        )
                
                messages.success(request, f'Vote session created! Share this link: {request.build_absolute_uri(reverse("vote", kwargs={"code": vote_session.code}))}') 
                return redirect('dashboard')
    else:
        session_form = VoteSessionForm()
    
    context = {
        'session_form': session_form,
        'categories': categories,
    }
    return render(request, 'voting/create_session.html', context)


def vote_view(request, code):
    """View for casting votes or viewing results"""
    vote_session = get_object_or_404(VoteSession, code=code)
    
    # Check if session is expired
    if vote_session.is_expired():
        messages.warning(request, 'This voting session has expired.')
        return redirect('home')
    
    # Check if polls are closed
    if vote_session.polls_closed:
        return redirect('results', code=code)
    
    # Handle user authentication
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to vote.')
        return redirect(f"{reverse('login')}?next={reverse('vote', kwargs={'code': code})}")
    
    # Check if user has already voted in this session
    user_votes = Vote.objects.filter(user=request.user, vote_session=vote_session)
    has_voted = user_votes.exists()
    
    if request.method == 'POST' and not has_voted:
        form = VoteForm(vote_session, request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create votes for each active category
                for cat in form.active_categories:
                    role = form.cleaned_data[cat['field_name']]
                    vote = Vote(
                        user=request.user,
                        role=role,
                        vote_session=vote_session
                    )
                    vote.save()
            
            messages.success(request, 'Your votes have been recorded!')
            return redirect('dashboard')
    else:
        form = VoteForm(vote_session)
    
    context = {
        'vote_session': vote_session,
        'form': form,
        'has_voted': has_voted
    }
    return render(request, 'voting/vote.html', context)


@login_required
def results_view(request, code):
    """View for showing voting results"""
    vote_session = get_object_or_404(VoteSession, code=code)
    
    # Check if user is admin or polls are closed
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not vote_session.polls_closed and not is_admin:
        messages.warning(request, 'Polls are still open. Results are not available yet.')
        return redirect('vote', code=code)
    
    # Get votes for each role type — only include categories that have participants
    results = {}
    for role_type, role_name in Role.ROLE_TYPES:
        roles = Role.objects.filter(vote_session=vote_session, role_type=role_type)
        if not roles.exists():
            continue
        votes = Vote.objects.filter(role__in=roles).values('role__name').annotate(count=Count('id')).order_by('-count')
        
        # Find winners (could be multiple in case of a tie)
        winners = []
        if votes:
            max_votes = votes[0]['count']
            winners = [v['role__name'] for v in votes if v['count'] == max_votes]
        
        results[role_type] = {
            'votes': list(votes),
            'winners': winners,
            'type_display': role_name
        }
    
    context = {
        'vote_session': vote_session,
        'results': results,
        'is_admin': is_admin
    }
    return render(request, 'voting/results.html', context)


@login_required
def manage_session(request, code):
    """View for managing a vote session (admin only)"""
    vote_session = get_object_or_404(VoteSession, code=code)
    
    # Check if the user is authorized to manage this session
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not is_admin or vote_session.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to manage this session.")
    
    context = {
        'vote_session': vote_session
    }
    return render(request, 'voting/manage_session.html', context)


@login_required
def close_polls(request, code):
    """AJAX view for closing polls"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    vote_session = get_object_or_404(VoteSession, code=code)
    
    # Check if the user is authorized to manage this session
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not is_admin or vote_session.created_by != request.user:
        return HttpResponseForbidden()
    
    # Close the polls
    vote_session.polls_closed = True
    vote_session.save()
    
    return HttpResponse(json.dumps({'success': True}), content_type='application/json')


@login_required
def toggle_results(request, code):
    """AJAX view for toggling result visibility"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    vote_session = get_object_or_404(VoteSession, code=code)
    
    # Check if the user is authorized to manage this session
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not is_admin or vote_session.created_by != request.user:
        return HttpResponseForbidden()
    
    # Toggle show_results
    vote_session.show_results = not vote_session.show_results
    vote_session.save()
    
    return HttpResponse(json.dumps({'show_results': vote_session.show_results}), content_type='application/json')


def timer_view(request):
    """Speech timer tool view"""
    return render(request, 'voting/timer.html')


def tabletopics_view(request):
    """Table Topics Master tool view"""
    return render(request, 'voting/tabletopics.html')
