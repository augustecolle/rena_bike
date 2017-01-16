mapboxgl.accessToken = 'pk.eyJ1IjoiYXVndXN0ZWNvbGxlIiwiYSI6ImNpeHE5b2p3YjAwMjgzM3AxYW11YTdqcm8ifQ.rWupKvdQ1UV6q4xJCBGKUw';

var map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/outdoors-v9',
  zoom: 18,
  center: [3.7174, 51.0543]
});
	
	
var directions = new MapboxDirections({
	accessToken: mapboxgl.accessToken,
  unit: 'metric', // Use the metric system to display distances.
	controls: {
		instructions: false,
	},
  profile: 'cycling', // Set the initial profile to walking.
  container: 'directions', // Specify an element thats not the map container.
  proximity: [3.7174, 51.0543] // Give search results closer to these coordinates higher priority.
});

function labelCurrentPosition(lat, lng){
	console.log("labelCurrentPosition");
	var el = document.createElement('div');
	//el.style.backgroundColor='red';
	el.style.backgroundImage = "url('images/rider.svg')";
	el.className = 'marker';
	el.style.width = '45' + 'px';
	el.style.height = '45' + 'px';
	var marker = new mapboxgl.Marker(el);
	marker.setLngLat([lng, lat]);
	marker.addTo(map);
	console.log(marker);
}

var positionIndicator

map.on('load', function () {
	var nav = new mapboxgl.NavigationControl();
	map.addControl(nav, 'bottom-left');
	console.log("onload function")
	//set center on current location with HTML5
	var pos;

	if (navigator.geolocation) {
	  navigator.geolocation.getCurrentPosition(function(position) {
			console.log("getting position")
	  	pos = {
	      lat: position.coords.latitude,
	      lng: position.coords.longitude
	    };
		map.setCenter([pos.lng, pos.lat]);
	  });
		postionIndicator = navigator.geolocation.watchPosition(function(position) {
			console.log("positionIndicator")
			labelCurrentPosition(position.coords.latitude, position.coords.longitude);
			console.log(position.coords.latitude, position.coords.longitude);
		});
	}
	map.addControl(directions);
});

function trackOnMap(lat, lng) {
	console.log("trackOnMap")
	map.setCenter([lng, lat]);
	map.setZoom(18);
}
directions.on('route', function(e) {
	console.log(e.route); // Logs the current route shown in the interface.
	var watchPosition = navigator.geolocation.watchPosition(function(position) {
		trackOnMap(position.coords.latitude, position.coords.longitude);
	});
});

