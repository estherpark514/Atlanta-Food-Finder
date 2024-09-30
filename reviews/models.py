# File: models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count

class Restaurant(models.Model):
    restaurant_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    opening_hours = models.JSONField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    icon = models.URLField(max_length=500, null=True, blank=True)
    vicinity = models.CharField(max_length=255, null=True, blank=True)
    total_ratings = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

    @staticmethod
    def save_restaurant_data(place):
        restaurant, created = Restaurant.objects.get_or_create(
            restaurant_id=place.get("place_id"),
            defaults={
                "name": place.get("name"),
                "opening_hours": place.get("opening_hours"),
                "rating": place.get("rating"),
                "price_level": place.get("price_level"),
                "icon": place.get("icon"),
                "vicinity": place.get("vicinity"),
                "total_ratings": place.get("user_ratings_total"),
            }
        )
        if created:
            print(f"Created restaurant: {restaurant.name}")
        else:
            print(f"Restaurant {restaurant.name} already exists.")
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(restaurant=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(restaurant=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class ReviewRating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # print(Account.objects.filter(id=request.user.id).exists())

    def __str__(self):
        return self.subject

class RestaurantGallery(models.Model):
    restaurant = models.ForeignKey(Restaurant, default=None, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"Image for {self.restaurant.name}"

    class Meta:
        verbose_name = 'restaurantgallery'
        verbose_name_plural = 'restaurant gallery'
