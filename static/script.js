let map;

function initMap() {
  // Initialize the map, centered on Atlanta
  const atlanta = { lat: 33.749, lng: -84.388 };
  map = new google.maps.Map(document.getElementById("map"), {
    center: atlanta,
    zoom: 12,
  });

  // Use Google Places API to fetch restaurants around Atlanta
  const service = new google.maps.places.PlacesService(map);
  const request = {
    location: atlanta,
    radius: "5000", // Adjust the radius as needed (5000 meters = 5 km)
    type: ["restaurant"],
  };

  // Search for restaurants and add markers
  service.nearbySearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
      const topThreeRestaurants=results
      .filter((place) => place.rating)
      .sort((a,b) => b.rating-a.rating)
      .slice(0, 3);

      if (topThreeRestaurants.length >= 3) {
        updateRestaurantProfile(1, topThreeRestaurants[0]);
        updateRestaurantProfile(2, topThreeRestaurants[1]);
        updateRestaurantProfile(3, topThreeRestaurants[2]);
      }

      results.forEach((restaurant) => createMarker(restaurant));
    } else {
      console.error("PlacesService failed: " + status);
    }
  });
}

function updateRestaurantProfile(profileNumber, restaurant) {
  const name = document.getElementById(`restaurant-name-${profileNumber}`);
  const location = document.getElementById(`restaurant-description-${profileNumber}`);
  const rating = document.getElementById(`restaurant-rating-${profileNumber}`);
  const ratingValue = document.getElementById(`rating-value-${profileNumber}`);

  name.textContent = restaurant.name; // Restaurant name
  location.textContent = `Located at ${restaurant.vicinity}, this restaurant is highly rated by our users!`;
  rating.setAttribute('data-rating', restaurant.rating); 
  ratingValue.textContent = restaurant.rating.toFixed(1);

  updateStarRatings(profileNumber, restaurant.rating);
}

function createMarker(place) {
  const marker = new google.maps.Marker({
      map: map,
      position: place.geometry.location,
      title: place.name,
  });

  const rating = place.rating ? `${place.rating} / 5` : "N/A";

  const infoWindow = new google.maps.InfoWindow({
      content: `
          <h3>${place.name}</h3>
          <p>${place.vicinity}</p>
          <p>Rating: ${rating}</p>
          <p>
              <i class="bx bxs-heart" style="cursor: pointer;" id="favorite-${place.place_id}" data-place-id="${place.place_id}"></i>
              <span id="favorite-text-${place.place_id}">Add to Favorites</span>
          </p>`,
  });

  marker.addListener("click", () => {
      infoWindow.open(map, marker);

      google.maps.event.addListenerOnce(infoWindow, "domready", () => {
          const heartIcon = document.getElementById(`favorite-${place.place_id}`);
          const favoriteText = document.getElementById(`favorite-text-${place.place_id}`);

          if (heartIcon) {
              heartIcon.addEventListener("click", function () {
                  addToFavorites(place, heartIcon, favoriteText);
              });
          } else {
              console.error(`Heart icon for ${place.name} not found.`);
          }
      });
  });
}

function addToFavorites(place, heartIcon, favoriteText) {
  const restaurantData = {
      place_id: place.place_id,
      name: place.name,
      vicinity: place.vicinity,
  };

  fetch(`/favorite/`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(restaurantData),
  }).then((response) => {
      if (response.ok) {
          alert(`${place.name} has been added to your favorites!`);
          // Change the heart icon's color and text
          heartIcon.classList.add("favorited"); // Mark as favorited
          favoriteText.textContent = 'Added to Favorite!s'; // Change button text
          favoriteText.style.color = 'red'; // Optional: Change text color to red
      } else {
          console.error("Error adding to favorites:", response.statusText);
      }
  });
}


// Function to load Google Maps API script dynamically with callback
function loadGoogleMapsScript() {
  const script = document.createElement("script");
  script.src =
    "https://maps.googleapis.com/maps/api/js?key=AIzaSyBLBtkghppVDE_9Sh29rCdHFIJOkq9F8V0&libraries=places&callback=initMap";
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function updateStarRatings(profileNumber, rating) {
  const roundedRating = parseFloat(rating.toFixed(1));
  
  const starElements = document.querySelectorAll(`#restaurant-profile-${profileNumber} .star-rating .star`);
  const fullStars = Math.floor(roundedRating);
  const partialStarPercentage = (roundedRating - fullStars) * 100;

  starElements.forEach((star, index) => {
    if (index < fullStars) {
      star.classList.add('filled');
      star.classList.remove('partially-filled');
      star.style.removeProperty('--partial-fill');
    } else if (index === fullStars && partialStarPercentage > 0) {
      star.classList.add('partially-filled');
      star.classList.remove('filled');
      star.style.setProperty('--partial-fill', `${partialStarPercentage}%`);
    } else {
      star.classList.remove('filled', 'partially-filled');
      star.style.removeProperty('--partial-fill');
    }
  });
}


document.addEventListener("DOMContentLoaded", function () {
  loadGoogleMapsScript();
});
