let map;
let restaurantsArray = []; // Array to store restaurant objects
let markersArray = []; // Array to store all markers for easy removal

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
        const topThreeRestaurants = results
          .filter((place) => place.rating)
          .sort((a, b) => b.rating - a.rating)
          .slice(0, 3);
  
        if (topThreeRestaurants.length >= 3) {
          updateRestaurantProfile(1, topThreeRestaurants[0]);
          updateRestaurantProfile(2, topThreeRestaurants[1]);
          updateRestaurantProfile(3, topThreeRestaurants[2]);
        }
  
        results.forEach((restaurant) => {
          restaurantsArray.push(restaurant); // Add restaurant to array
          createMarker(restaurant); // Create a marker for each restaurant
        });
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
  const image = document.getElementById(`restaurant-image-${profileNumber}`);
  const detailsButton = document.getElementById(`details-button-${profileNumber}`);

  name.textContent = restaurant.name;
  location.textContent = `Located at ${restaurant.vicinity}, this restaurant is highly rated by our users!`;
  rating.setAttribute('data-rating', restaurant.rating);
  ratingValue.textContent = restaurant.rating.toFixed(1);
  if (detailsButton) {
    detailsButton.href = `/detail/${restaurant.place_id}/`;
  }

  updateStarRatings(profileNumber, restaurant.rating);

  if (Array.isArray(restaurant.photos) && restaurant.photos.length > 0) {
    const firstPhoto = restaurant.photos[0];
    const imageUrl = firstPhoto.getUrl({ maxWidth: 600, maxHeight: 600 });

    image.innerHTML = `<img src="${imageUrl}" alt="${restaurant.name}" style="width:100%; height:300px;">`;
  } else {
    image.innerHTML = `<p>No image available</p>`;
  }
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
          <span id="favorite-text-${place.place_id}" style="cursor: pointer;">Add to Favorites</span>
      </p>
      <p>
          <a href="/detail/${place.place_id}/" style="color: black; text-decoration: none;">
              View Details <span style="text-transform: none">&rarr;</span>
          </a>
      </p>
    `,
  });

  marker.addListener("click", () => {
    infoWindow.open(map, marker);

    google.maps.event.addListenerOnce(infoWindow, "domready", () => {
      const heartIcon = document.getElementById(`favorite-${place.place_id}`);
      const favoriteText = document.getElementById(`favorite-text-${place.place_id}`);

      if (heartIcon && favoriteText) {
        const clickHandler = function () {
          addToFavoritesMap(place, heartIcon, favoriteText);
        };

        heartIcon.addEventListener("click", clickHandler);
        favoriteText.addEventListener("click", clickHandler);
      } else {
        console.error(`Heart icon or favorite text for ${place.name} not found.`);
      }
    });
  });

  markersArray.push(marker);
}

// Function to filter restaurants by search query
function filterRestaurants(query) {
  clearMarkers(); // Clear existing markers from the map

  // Filter restaurants by query (case-insensitive)
  const filteredRestaurants = restaurantsArray.filter((restaurant) =>
    restaurant.name.toLowerCase().includes(query.toLowerCase())
  );

  // Create markers for the filtered restaurants
  filteredRestaurants.forEach((restaurant) => createMarker(restaurant));
}

// Function to clear all existing markers from the map
function clearMarkers() {
  markersArray.forEach((marker) => {
    marker.setMap(null);
  });
  markersArray = []; // Reset the markers array
}

// Event listener for search form submission
document.getElementById("search-form").addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent the form from submitting the traditional way
  const query = document.getElementById("search-input").value; // Get the query from the search input
  filterRestaurants(query); // Filter and display matching restaurants
});

// Event listener for reset button
document.getElementById("reset-btn").addEventListener("click", () => {
  document.getElementById("search-input").value = ""; // Clear search input
  clearMarkers(); // Clear current markers
  restaurantsArray.forEach((restaurant) => createMarker(restaurant)); // Reload all restaurants on the map
});

function addToFavoritesMap(place, heartIcon, favoriteText) {
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
          heartIcon.classList.add("favorited");
          heartIcon.style.color = 'red';
          favoriteText.textContent = 'Added to Favorites!'; 
          favoriteText.style.color = 'red'; 
      } else {
          console.error("Error adding to favorites:", response.statusText);
      }
  });
}

function addToFavorites(place, button) {
  // Fetch request to add the place to favorites
  fetch(`/favorite/`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(place),
  }).then((response) => {
      if (response.ok) {
          button.textContent = 'Added to Favorites!';
          button.style.backgroundColor = 'green';
          button.style.color = 'white'; 
          button.disabled = true;
      } else {
          console.error("Error adding to favorites:", response.statusText);
          alert("Failed to add to favorites. Please try again later.");
      }
  }).catch((error) => {
      console.error("Network error:", error);
      alert("There was a network issue. Please try again.");
  });
}

document.addEventListener('DOMContentLoaded', function () {
  const favoriteButton = document.getElementById('button');
  
  if (favoriteButton) {
      favoriteButton.addEventListener('click', function(event) {
          event.preventDefault();
          
          const place = {
              place_id: this.getAttribute('data-place-id'),
              name: this.getAttribute('data-name'),
              vicinity: this.getAttribute('data-vicinity'),
          };

          addToFavorites(place, this);
      });
  } else {
      console.error("Button element not found!");
  }
});




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

document.getElementById('logoutBtn').addEventListener('click', function() {
  fetch('/logout/', { 
      method: 'POST', 
      credentials: 'include',
      headers: {
          'X-CSRFToken': getCookie('csrftoken'), 
      }
  })
  .then(response => {
      if (response.ok) {
          window.location.href = loginUrl;
      } else {
          alert('Logout failed. Please try again.');
      }
  })
  .catch(error => console.error('Error:', error));
});

