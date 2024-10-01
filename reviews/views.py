from django.shortcuts import render, redirect
from .models import Restaurant, ReviewRating, RestaurantGallery
from .services import fetch_restaurants_from_api, fetch_place_details
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
        places = fetch_restaurants_from_api(api_key, location, radius)

        if places:
            for place in places:
                restaurant_id = place.get('place_id')
                place_details = fetch_place_details(restaurant_id, api_key)
                phone_number = place_details.get('formatted_phone_number', 'Not available')
                cuisine_type_list = place_details.get('types', [])
                cuisine_type = ", ".join(cuisine_type_list) if cuisine_type_list else 'Not available'
                latitude = round(place_details.get('geometry', {}).get('location', {}).get('lat', 0), 2)
                longitude = round(place_details.get('geometry', {}).get('location', {}).get('lng', 0), 2)
                
                address_components = place_details.get('address_components', [])
                fourth_component_long_name = address_components[2].get('long_name', 'Not available') if len(address_components) > 3 else 'Not available'

                print(f"Name: {place.get('name')}, Location: {fourth_component_long_name}")
                try:
                    restaurant, created = Restaurant.objects.get_or_create(
                        restaurant_id=restaurant_id,
                        defaults={
                            'name': place.get('name'),
                            'price_level': place.get('price_level'),
                            'icon': place.get('icon'),
                            'vicinity': place.get('vicinity'),
                            'total_ratings': place.get('user_ratings_total', 0),
                            'phone_number': phone_number,
                            'latitude': latitude,
                            'longitude': longitude,
                            'cuisine_type': cuisine_type,
                            'region':fourth_component_long_name,
                        }
                    )
                    # print(f"Saved restaurant with ID: {restaurant.restaurant_id}, "
                    #       f"Name: {restaurant.name}, "
                    #       f"Latitude: {restaurant.latitude}, "
                    #       f"Longitude: {restaurant.longitude}, "
                    #       f"Phone Number: {restaurant.phone_number}, "
                    #       f"Cuisine Type: {restaurant.cuisine_type}")
                    if created:
                        print(f"Created new restaurant: {restaurant.name}, Location: {restaurant.location}")
                    else:
                        # Update the existing restaurant's details
                        restaurant.name = place.get('name', restaurant.name)
                        restaurant.price_level = place.get('price_level', restaurant.price_level)
                        restaurant.icon = place.get('icon', restaurant.icon)
                        restaurant.vicinity = place.get('vicinity', restaurant.vicinity)
                        restaurant.total_ratings = place.get('user_ratings_total', restaurant.total_ratings)
                        restaurant.phone_number = phone_number or restaurant.phone_number 
                        restaurant.latitude = latitude or restaurant.latitude
                        restaurant.longitude = longitude or restaurant.longitude
                        restaurant.cuisine_type = cuisine_type or restaurant.cuisine_type
                        restaurant.region = fourth_component_long_name
                        
                        # Save the updated restaurant
                        restaurant.save()
                        # print(f"Updated existing restaurant: {restaurant.name}, New Location: {restaurant.location}")
                except Exception as e:
                    print(f"Error saving restaurant: {e}")
                if 'photos' in place:
                    for photo in place['photos']:
                        photo_reference = photo.get('photo_reference')
                        if photo_reference:
                            image_url = f"{photo_base_url}?maxwidth=600&photoreference={photo_reference}&key={api_key}"
                            RestaurantGallery.objects.create(
                                restaurant=restaurant,
                                image_url=image_url
                            )
                            # print(f"Saved image URL: {image_url}")
                else:
                    print("No photos found for this restaurant.")

            return 'Restaurants fetched and saved successfully!'
        else:
            return 'No restaurants found.'

    except Exception as e:
        # print(f"An error occurred: {str(e)}")
        return f'An error occurred: {str(e)}'

def restaurant_detail(request, restaurant_id):
    try:
        message = fetch_and_save_restaurants()
        # print(f"Fetch message: {message}") 

        restaurant = get_object_or_404(Restaurant, restaurant_id=restaurant_id)
        reviews = ReviewRating.objects.filter(restaurant=restaurant)
        restaurant_gallery = RestaurantGallery.objects.filter(restaurant=restaurant)

        first_image_url = None
        if restaurant_gallery.exists():
            first_photo = restaurant_gallery.first()
            first_image_url = first_photo.image_url

        context = {
            'restaurant': restaurant,
            'reviews': reviews,
            'restaurant_gallery': restaurant_gallery,
            'first_image_url': first_image_url,
            'address': restaurant.vicinity if restaurant.vicinity else "Not available",
            'contact_info': restaurant.phone_number if restaurant.phone_number else "Not available",
            'cuisine_type': restaurant.cuisine_type if restaurant.cuisine_type else "Not available",
            'longitude': restaurant.longitude if restaurant.longitude else "Not available",
            'latitude': restaurant.latitude if restaurant.latitude else "Not available",
        }
        # print(f"Final Restaurant Latitude: {restaurant.latitude}, Restaurant Longitude: {restaurant.longitude}")

        return render(request, 'detail.html', context)
    
    except Exception as e:
        # print(f"An error occurred while fetching restaurant details: {str(e)}")  # Log the error
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

