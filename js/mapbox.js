function mapbox(){
  
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
    proximity: [-79.45, 43.65] // Give search results closer to these coordinates higher priority.
  });


  map.on('load', function () {
    var nav = new mapboxgl.NavigationControl();
    map.addControl(nav, 'bottom-left');
    //add GEolocateControl
    //map.addControl(new mapboxgl.GeolocateControl({
    //  positionOptions: {
    //    enableHighAccuracy: true
    //  },
    //	watchPosition: true
    //	}));
    ////add geocoder

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
    }

    map.addControl(directions);

  });

  directions.on('route', function(e) {
    console.log(e.route); // Logs the current route shown in the interface.
  });

}

