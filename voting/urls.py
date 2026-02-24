from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='voting/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-session/', views.create_vote_session, name='create_session'),
    path('vote/<str:code>/', views.vote_view, name='vote'),
    path('results/<str:code>/', views.results_view, name='results'),
    path('manage/<str:code>/', views.manage_session, name='manage_session'),
    path('close-polls/<str:code>/', views.close_polls, name='close_polls'),
    path('toggle-results/<str:code>/', views.toggle_results, name='toggle_results'),
]
