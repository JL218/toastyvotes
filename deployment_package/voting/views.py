from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Count
from django.db import transaction
from django.forms import modelformset_factory
from .models import VoteSession, Role, Vote, AdminProfile
from .forms import UserRegistrationForm, VoteSessionForm, RoleForm, VoteForm
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
    
    if is_admin:
        # For admins, show their created vote sessions
        vote_sessions = VoteSession.objects.filter(created_by=request.user)
    else:
        # For regular users, show their votes
        user_votes = Vote.objects.filter(user=request.user)
        vote_sessions = VoteSession.objects.filter(votes__in=user_votes).distinct()
    
    context = {
        'vote_sessions': vote_sessions,
        'is_admin': is_admin
    }
    return render(request, 'voting/dashboard.html', context)


@login_required
def create_vote_session(request):
    """View for creating a new vote session (admin only)"""
    # Check if the user is a platform admin
    is_admin = hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_platform_admin
    if not is_admin:
        return HttpResponseForbidden("You must be an admin to create vote sessions.")
    
    # Create formset for roles
    RoleFormSet = modelformset_factory(Role, form=RoleForm, extra=6, max_num=6)
    
    if request.method == 'POST':
        session_form = VoteSessionForm(request.POST)
        role_formset = RoleFormSet(request.POST, prefix='roles')
        
        if session_form.is_valid() and role_formset.is_valid():
            with transaction.atomic():
                # Save the vote session
                vote_session = session_form.save(commit=False)
                vote_session.created_by = request.user
                vote_session.expires_at = timezone.now() + timezone.timedelta(hours=24)
                vote_session.save()
                
                # Create roles - 2 of each type
                role_types = ['SPEAKER', 'EVALUATOR', 'TABLE_TOPICS']
                positions = [1, 2]
                
                # Process formset data
                instances = role_formset.save(commit=False)
                for i, instance in enumerate(instances):
                    role_type_index = i // 2  # 0, 0, 1, 1, 2, 2
                    position = (i % 2) + 1  # 1, 2, 1, 2, 1, 2
                    
                    instance.vote_session = vote_session
                    instance.role_type = role_types[role_type_index]
                    instance.position = position
                    instance.save()
            
            messages.success(request, f'Vote session created! Share this link: {request.build_absolute_uri(reverse("vote", kwargs={"code": vote_session.code}))}') 
            return redirect('dashboard')
    else:
        session_form = VoteSessionForm()
        role_formset = RoleFormSet(queryset=Role.objects.none(), prefix='roles')
    
    # Pre-fill form labels to match expected roles
    role_forms = role_formset.forms
    role_labels = [
        'Speaker 1', 'Speaker 2',
        'Evaluator 1', 'Evaluator 2',
        'Table Topics Master 1', 'Table Topics Master 2'
    ]
    
    context = {
        'session_form': session_form,
        'role_formset': role_formset,
        'role_forms': zip(role_forms, role_labels) if len(role_forms) == 6 else None
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
                # Create votes for each category
                for category, role_id in form.cleaned_data.items():
                    vote = Vote(
                        user=request.user,
                        role=role_id,
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
    
    # Get votes for each role type
    results = {}
    for role_type, role_name in Role.ROLE_TYPES:
        roles = Role.objects.filter(vote_session=vote_session, role_type=role_type)
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
