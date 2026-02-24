from django.contrib import admin
from .models import VoteSession, Role, Vote, AdminProfile


@admin.register(VoteSession)
class VoteSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_by', 'created_at', 'expires_at', 'is_active', 'polls_closed')
    list_filter = ('is_active', 'polls_closed', 'created_at')
    search_fields = ('title', 'code', 'created_by__username')
    date_hierarchy = 'created_at'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_type', 'position', 'vote_session')
    list_filter = ('role_type', 'vote_session')
    search_fields = ('name', 'vote_session__code')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'vote_session', 'timestamp')
    list_filter = ('vote_session', 'role__role_type', 'timestamp')
    search_fields = ('user__username', 'role__name', 'vote_session__code')
    date_hierarchy = 'timestamp'


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_platform_admin')
    list_filter = ('is_platform_admin',)
    search_fields = ('user__username', 'user__email')
