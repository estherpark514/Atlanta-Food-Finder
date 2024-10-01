from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reviews.models import ReviewRating, Restaurant
import json
import logging
from .models import *

# Renders the home page (index.html) if the user is logged in
@login_required
def Home(request):
    restaurants = Restaurant.objects.all()
    # print(f"Total restaurants: {restaurants.count()}") 
    # for restaurant in restaurants:
    #     region = getattr(restaurant, 'region', 'Not available')
    #     print(f"Name: {restaurant.name}, Region: {restaurant.restaurant_id}")
    return render(request, 'index.html', {'restaurants': restaurants})


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

def Profile(request):
    favorites = FavoriteRestaurant.objects.filter(user=request.user).select_related('restaurant')
    comments = ReviewRating.objects.filter(user=request.user)  # Fetch the user's comments
    
    return render(request, 'profile.html', {'favorites': favorites, 'comments': comments})


logger = logging.getLogger(__name__)

@csrf_exempt  # Only use this if you are handling CSRF manually
def add_to_favorites(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)

            # Validate the incoming data
            if 'place_id' not in data or 'name' not in data or 'vicinity' not in data:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

            # Get or create the restaurant object
            restaurant, created = Restaurant.objects.get_or_create(
                place_id=data['place_id'],
                defaults={'name': data['name'], 'vicinity': data['vicinity']}
            )

            # Get or create the favorite restaurant entry for the current user
            favorite, created = FavoriteRestaurant.objects.get_or_create(user=request.user, restaurant=restaurant)

            # Return a success message
            return JsonResponse({'status': 'success', 'message': 'Added to favorites!'})

        except json.JSONDecodeError:
            logger.error("JSON decode error: Invalid JSON received.")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)