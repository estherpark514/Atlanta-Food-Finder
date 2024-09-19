// Initialize and add the map
function initMap() {
  // The location of Atlanta
  var atlanta = { lat: 33.749, lng: -84.388 };

  // The map, centered at Atlanta
  var map = new google.maps.Map(document.getElementById("map"), {
    zoom: 12,
    center: atlanta,
  });

  // The marker, positioned at Atlanta
  var marker = new google.maps.Marker({
    position: atlanta,
    map: map,
  });
}

// Function to load Google Maps API script
function loadGoogleMapsScript() {
  var script = document.createElement("script");
  script.src =
    "https://maps.googleapis.com/maps/api/js?key=AIzaSyBKq25ooRZTBr-7RsbX60Mzl1OFZgqePuE&callback=initMap";
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
