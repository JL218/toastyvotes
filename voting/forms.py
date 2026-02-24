from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import VoteSession, Role, Vote


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class VoteSessionForm(forms.ModelForm):
    """Form for creating a vote session"""
    class Meta:
        model = VoteSession
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting Title'})
        }


class RoleForm(forms.ModelForm):
    """Form for adding a role"""
    class Meta:
        model = Role
        fields = ('name', 'role_type', 'position')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Person Name'}),
            'role_type': forms.HiddenInput(),
            'position': forms.HiddenInput(),
        }


class VoteForm(forms.Form):
    """Dynamic form for submitting votes — only includes categories that have participants"""

    CATEGORY_CONFIG = {
        'SPEAKER': {'label': 'Best Speaker', 'field_name': 'speaker'},
        'EVALUATOR': {'label': 'Best Evaluator', 'field_name': 'evaluator'},
        'TABLE_TOPICS': {'label': 'Best Table Topics Speaker', 'field_name': 'table_topics'},
    }

    def __init__(self, vote_session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vote_session = vote_session
        self.active_categories = []

        for role_type, config in self.CATEGORY_CONFIG.items():
            qs = Role.objects.filter(vote_session=vote_session, role_type=role_type)
            if qs.exists():
                self.fields[config['field_name']] = forms.ModelChoiceField(
                    queryset=qs,
                    widget=forms.RadioSelect,
                    required=True,
                    empty_label=None,
                    label=config['label'],
                )
                self.active_categories.append({
                    'field_name': config['field_name'],
                    'label': config['label'],
                    'role_type': role_type,
                })
