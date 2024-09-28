from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import AbstractBaseUser


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_time}"
    
class Restaurant(models.Model):
    place_id = models.CharField(max_length=255, unique=True, null=True)  # Add this line
    name = models.CharField(max_length=255)
    vicinity = models.CharField(max_length=255, null=True)  # Add this line if you need vicinity
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)  # Keep as optional if needed

    def __str__(self):
        return self.name

class FavoriteRestaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.restaurant.name}'

class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=100, unique=True)

    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email