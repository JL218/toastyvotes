from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


def generate_random_code(length=4):
    """Generate a random alphanumeric code"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class Role(models.Model):
    """Model representing a role that can be voted for"""
    ROLE_TYPES = [
        ('SPEAKER', 'Speaker'),
        ('EVALUATOR', 'Evaluator'),
        ('TABLE_TOPICS', 'Table Topics Master'),
    ]
    
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES)
    position = models.IntegerField(default=1)  # 1 or 2 for each role type
    vote_session = models.ForeignKey('VoteSession', on_delete=models.CASCADE, related_name='roles')
    
    class Meta:
        unique_together = ['vote_session', 'role_type', 'position']
        ordering = ['role_type', 'position']
    
    def __str__(self):
        return f"{self.get_role_type_display()} {self.position}: {self.name}"


class VoteSession(models.Model):
    """Model representing a voting session"""
    title = models.CharField(max_length=200, default="Toastmasters Vote")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    code = models.CharField(max_length=10, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    polls_closed = models.BooleanField(default=False)
    show_results = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Generate a random code if one doesn't exist
        if not self.code:
            self.code = generate_random_code()
        
        # Set expiration date to 24 hours from now if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Vote Session: {self.code} ({self.title})"


class Vote(models.Model):
    """Model representing a user's vote for a role"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='votes')
    vote_session = models.ForeignKey(VoteSession, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Proper constraint that allows one vote per user per role type per session
        unique_together = ['user', 'vote_session', 'role']
    
    def save(self, *args, **kwargs):
        # Check if the user already voted for this role type in this session
        existing_votes = Vote.objects.filter(
            user=self.user,
            vote_session=self.vote_session,
            role__role_type=self.role.role_type
        ).exclude(pk=self.pk)
        
        if existing_votes.exists():
            from django.core.exceptions import ValidationError
            raise ValidationError(f"You have already voted for a {self.role.get_role_type_display()} in this session.")
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} voted for {self.role.name} as {self.role.get_role_type_display()}"


class AdminProfile(models.Model):
    """Model extending the User model for platform admins"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    is_platform_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_platform_admin else 'User'}"
