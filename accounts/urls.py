from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('keep-alive/', views.keep_alive, name='keep_alive'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]
