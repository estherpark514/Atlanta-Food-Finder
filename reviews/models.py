# File: models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count

class Restaurant(models.Model):
    restaurant_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    opening_hours = models.JSONField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    icon = models.URLField(max_length=500, null=True, blank=True)
    vicinity = models.CharField(max_length=255, null=True, blank=True)
    total_ratings = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    cuisine_type = models.TextField(null=True, blank=True) 
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    region = models.TextField(null=True, blank=True) 

    def __str__(self):
        return self.name

    @staticmethod
    def save_restaurant_data(place):
        try:
            address_components = place.get('address_components', [])
            location = None
            for component in address_components:
                if 'locality' in component.get('types', []):
                    location = component.get('long_name')
                    break
                elif 'administrative_area_level_1' in component.get('types', []):
                    location = component.get('long_name')

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
                    "phone_number": place.get("formatted_phone_number"),
                    "cuisine_type": ", ".join(place.get("types", [])),
                    "latitude": place.get('geometry', {}).get('location', {}).get('lat'),
                    "longitude": place.get('geometry', {}).get('location', {}).get('lng'),
                    "region": location,
                }
            )
            if created:
                print(f"Created restaurant: {restaurant.name}")
            else:
                print(f"Saved restaurant with ID: {restaurant.restaurant_id}, "
                          f"Name: {restaurant.name}, "
                          f"Latitude: {restaurant.latitude}, "
                          f"Longitude: {restaurant.longitude}, "
                          f"Phone Number: {restaurant.phone_number}, "
                          f"Region Type: {restaurant.region}")
        except Exception as e:
            print(f"Error saving restaurant data: {e}")

    def average_review(self):
        reviews = ReviewRating.objects.filter(restaurant=self, status=True).aggregate(average=Avg('rating'))
        return float(reviews['average']) if reviews['average'] is not None else 0.0

    def count_review(self):
        reviews = ReviewRating.objects.filter(restaurant=self, status=True).aggregate(count=Count('id'))
        return int(reviews['count']) if reviews['count'] is not None else 0


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
