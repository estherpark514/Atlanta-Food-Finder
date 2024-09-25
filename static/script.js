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
      for (let i = 0; i < results.length; i++) {
        createMarker(results[i]);
      }
    } else {
      console.error("PlacesService failed: " + status);
    }
  });
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

function handleStarRatings() {
  const starRatings = document.querySelectorAll(".star-rating");

  starRatings.forEach((starRating) => {
    const rating = parseFloat(starRating.getAttribute("data-rating"));

    if (isNaN(rating)) {
      console.error("Invalid rating value");
      return;
    }

    const fullStars = Math.floor(rating);
    const partialStarPercentage = (rating - fullStars) * 100;
    // console.log(`Star percentage rounded: ${partialStarPercentage}`);

    const stars = starRating.querySelectorAll(".star");

    stars.forEach((star, index) => {
      if (index < fullStars) {
        star.classList.add("filled");
        star.classList.remove("partially-filled");
      } else if (index === fullStars) {
        star.classList.add("partially-filled");
        star.classList.remove("filled");
        star.style.setProperty("--partial-fill", `${partialStarPercentage}%`);
      } else {
        star.classList.remove("filled", "partially-filled");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  handleStarRatings();
  loadGoogleMapsScript();
});
