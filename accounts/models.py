from django.db import models
from django.contrib.auth.models import User
import uuid

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
