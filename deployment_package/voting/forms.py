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


class RoleFormSet(forms.BaseModelFormSet):
    """Formset for adding roles to a vote session"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Role.objects.none()


class RoleForm(forms.ModelForm):
    """Form for adding a role"""
    class Meta:
        model = Role
        fields = ('name', 'role_type', 'position')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Person Name'}),
            'role_type': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}, choices=[(1, '1'), (2, '2')])
        }


class VoteForm(forms.Form):
    """Form for submitting votes"""
    speaker = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        required=True,
        empty_label=None
    )
    evaluator = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        required=True,
        empty_label=None
    )
    table_topics = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        required=True,
        empty_label=None,
        label='Table Topics Master'
    )

    def __init__(self, vote_session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['speaker'].queryset = Role.objects.filter(
            vote_session=vote_session, 
            role_type='SPEAKER'
        )
        self.fields['evaluator'].queryset = Role.objects.filter(
            vote_session=vote_session, 
            role_type='EVALUATOR'
        )
        self.fields['table_topics'].queryset = Role.objects.filter(
            vote_session=vote_session, 
            role_type='TABLE_TOPICS'
        )
