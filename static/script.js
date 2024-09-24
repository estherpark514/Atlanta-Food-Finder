let map;

function initMap() {
  // Initialize the map, centered on Atlanta
  const atlanta = { lat: 33.7490, lng: -84.3880 };
  map = new google.maps.Map(document.getElementById("map"), {
    center: atlanta,
    zoom: 12,
  });

  // Use Google Places API to fetch restaurants around Atlanta
  const service = new google.maps.places.PlacesService(map);
  const request = {
    location: atlanta,
    radius: '5000', // Adjust the radius as needed (5000 meters = 5 km)
    type: ['restaurant'],
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

// Create a marker for each restaurant
function createMarker(place) {
  const marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location,
    title: place.name,
  });

  // Get the rating, or show 'N/A' if no rating is available
  const rating = place.rating ? `${place.rating} / 5` : 'N/A';

  // Create an info window to display restaurant details including the rating
  const infoWindow = new google.maps.InfoWindow({
    content: `<h3>${place.name}</h3><p>${place.vicinity}</p><p>Rating: ${rating}</p>`,
  });

  // Add a click event to open the info window when a marker is clicked
  marker.addListener("click", () => {
    infoWindow.open(map, marker);
  });
}

// Function to load Google Maps API script dynamically with callback
function loadGoogleMapsScript() {
  const script = document.createElement("script");
  script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyBLBtkghppVDE_9Sh29rCdHFIJOkq9F8V0&libraries=places&callback=initMap";
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
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
