from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegisterView, name='register'),
    path('home/', views.Home, name='home'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('profile/', views.Profile, name='profile'),
    path('favorite/', views.add_to_favorites, name='add_to_favorites'),
]