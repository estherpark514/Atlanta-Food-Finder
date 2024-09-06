from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import *

@login_required

# Renders the home page (index.html) if the user is logged in
def Home(request):
    return render(request, 'index.html')

# Handles user registration, including validation and account creation
def RegisterView(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        register_error = False

        # Check for existing username and email, and validate password length
        if User.objects.filter(username=username).exists():
            register_error = True
            messages.error(request, "Username already exists")

        if User.objects.filter(email=email).exists():
            register_error = True
            messages.error(request, "Email already exists")

        if len(password) < 8:
            register_error = True
            messages.error(request, "Password must be at least 8 characters")

        # If errors exist, redirect to registration page. Otherwise, create a new user
        if register_error:
            return redirect('register')
        
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email, 
                username=username,
                password=password
            )
            messages.success(request, "Account created. Login now")
            return redirect('login')

    return render(request, 'register.html')

# Handles user login by authenticating credentials and redirecting to the home page
def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        # If authentication is successful, log the user in. Otherwise, show an error message
        if user is not None:
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'login.html')

# Logs the user out and redirects to the login page
def LogoutView(request):
    logout(request)

    return redirect('login')

# Handles the process of initiating a password reset by sending a reset link to the user's email
def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            new_password = PasswordReset(user=user)
            new_password.save()
            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'

            # Send the password reset email to the user
            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email_message.fail_silently = True
            email_message.send()
            return redirect('password-reset-sent', reset_id=new_password.reset_id)

        # If the email is not found, display an error message
        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')

# Displays a confirmation page after the password reset link is sent if the reset ID is valid
def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    
    # If the reset ID is invalid, show an error and redirect to forgot-password page
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

# Handles the actual password reset process, including validation and updating the user's password
def ResetPassword(request, reset_id):

    try:
        reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            password_error = False

            # Validate that passwords match and meet length requirements
            if password != confirm_password:
                password_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 8:
                password_error = True
                messages.error(request, 'Password must be at least 8 characters long')

            # Check if the reset link has expired
            expiration_time = reset_id.created_time + timezone.timedelta(hours=24)

            if timezone.now() > expiration_time:
                password_error = True
                messages.error(request, 'Reset link has expired')
                reset_id.delete()

            # If no errors, update the user's password and delete the reset ID
            if not password_error:
                user = reset_id.user
                user.set_password(password)
                user.save()
                reset_id.delete()
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')

            else:
                return redirect('reset-password', reset_id=reset_id)

    # If the reset ID is invalid, show an error and redirect to forgot-password page
    except PasswordReset.DoesNotExist:        
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')