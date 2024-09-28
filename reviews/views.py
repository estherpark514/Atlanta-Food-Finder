from django.shortcuts import render, redirect
from .models import Restaurant, ReviewRating, RestaurantGallery
from .services import fetch_restaurants_from_api
from .forms import ReviewForm
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def fetch_and_save_restaurants():
    api_key = 'AIzaSyA6l8IHzzyZ8qa0uM2syPh5gSNMQ7g8jmo'
    location = "33.749,-84.388"
    radius = 5000
    photo_base_url = "https://maps.googleapis.com/maps/api/place/photo"

    try:
        # print("Fetching restaurants from API...")
        places = fetch_restaurants_from_api(api_key, location, radius)

        if places:
            # print(f"Found {len(places)} restaurants.")
            for place in places:
                # print(f"Processing restaurant: {place}")
                restaurant_id = place.get('place_id')  
                restaurant, created = Restaurant.objects.get_or_create(
                    restaurant_id=restaurant_id,
                    defaults={
                        'name': place.get('name'),
                        'opening_hours': place.get('opening_hours'),
                        'rating': place.get('rating'),
                        'price_level': place.get('price_level'),
                        'icon': place.get('icon'),
                        'vicinity': place.get('vicinity'),
                        'total_ratings': place.get('user_ratings_total', 0),
                    }
                )
                if created:
                    print(f"Created new restaurant: {place['name']}") 

                else:
                    print(f"Restaurant already exists: {place['name']}")

                if 'photos' in place:
                    for photo in place['photos']:
                        photo_reference = photo.get('photo_reference')
                        if photo_reference:
                            # Generate image URL
                            image_url = f"{photo_base_url}?maxwidth=600&photoreference={photo_reference}&key={api_key}"
                            
                            # Save the image URL without checking for duplicates
                            RestaurantGallery.objects.create(
                                restaurant=restaurant,
                                image_url=image_url
                            )
                            print(f"Saved image URL: {image_url}")
                else:
                    print(f"No photos available for {place.get('name')}")

            # print("All restaurants processed.")

            return 'Restaurants fetched and saved successfully!'
        else:
            print("No restaurants found.") 
            return 'No restaurants found.' 

    except Exception as e:
        print(f"An error occurred: {str(e)}")  
        return f'An error occurred: {str(e)}' 


def restaurant_detail(request, restaurant_id):
    # print("Starting restaurant detail view.")
    # print(f"Fetching restaurant with ID: {restaurant_id}")
    try:
        # print(f"Fetching restaurant with ID: {restaurant_id}")

        message = fetch_and_save_restaurants()
        print(f"Fetch message: {message}") 

        # Get restaurant by restaurant_id
        restaurant = get_object_or_404(Restaurant, restaurant_id=restaurant_id)
        reviews = ReviewRating.objects.filter(restaurant=restaurant)
        restaurant_gallery = RestaurantGallery.objects.filter(restaurant=restaurant)

        print(f"Number of images in gallery: {restaurant_gallery.count()}")

        first_image_url = None
        if restaurant_gallery.exists():
            first_photo = restaurant_gallery.first()
            first_image_url = first_photo.image_url
            print(f"First image URL: {first_image_url}")

        context = {
            'restaurant': restaurant,
            'reviews': reviews,
            'restaurant_gallery': restaurant_gallery,
            'first_image_url': first_image_url,
        }
        return render(request, 'detail.html', context)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Log the error
        return HttpResponse("An error occurred while fetching restaurant details.")

@login_required
def submit_review(request, restaurant_id):
    url = request.META.get('HTTP_REFERER')
    
    # Check if the restaurant exists
    if not Restaurant.objects.filter(id=restaurant_id).exists():
        messages.error(request, 'Restaurant does not exist.')
        return redirect(url)

    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, restaurant_id=restaurant_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
                return redirect(url)
            else:
                print("Form errors:", form.errors)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                print("Form data:", form.cleaned_data)
                print("User ID:", request.user.id)
                print("Restaurant ID:", restaurant_id)

                # Check if the user exists
                if not User.objects.filter(id=request.user.id).exists():
                    messages.error(request, 'User does not exist.')
                    return redirect(url)

                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.restaurant_id = restaurant_id
                data.user_id = request.user.id

                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                print("Form errors:", form.errors)

