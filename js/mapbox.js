//VARIABLES
//var rider;
//var map;

function mapbox($http, $rootScope){
  mapboxgl.accessToken = 'pk.eyJ1IjoiYXVndXN0ZWNvbGxlIiwiYSI6ImNpeHE5b2p3YjAwMjgzM3AxYW11YTdqcm8ifQ.rWupKvdQ1UV6q4xJCBGKUw';

  var pos;
  map = new mapboxgl.Map({
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
    var el = document.createElement('div');
    //el.style.backgroundColor='red';
    el.style.backgroundImage = "url('images/rider.svg')";
    el.className = 'marker';
    el.id = 'rider';
    el.style.width = '45' + 'px';
    el.style.height = '45' + 'px';
    var marker = new mapboxgl.Marker(el);
    marker.setLngLat([lng, lat]);
    marker.addTo(map);
    return marker;
  }

  var positionIndicator;
  var rider;
  map.on('load', function () {
    var nav = new mapboxgl.NavigationControl();
    map.addControl(nav, 'bottom-left');
    //set center on current location with HTML5
    if (navigator.geolocation) {

      navigator.geolocation.getCurrentPosition(function(position) {
        pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        rider = labelCurrentPosition(position.coords.latitude, position.coords.longitude);
        map.setCenter([pos.lng, pos.lat]);
        startPositionWatch();
      }, function(error){
        alert("Error loading position: " + error);
      }, {timeout:10000});

      startPositionWatch = function(){
        postionIndicator = navigator.geolocation.watchPosition(function(position) {
          rider.setLngLat([position.coords.longitude, position.coords.latitude]);
        }, function(error){
          alert("Error loading position: " + error);
        }, {timeout:10000});
      }
    } else {
      alert("No geolocation supported");
    }
    map.addControl(directions);
    map.addControl(new mapboxgl.GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true,
        watchPosition: true
      }
    }), 'bottom-right');
  });

  directions.on('route', function(e) {
    var parameter = e.route;

    url = "https://"+location.hostname+":5000/Trajectory"
    console.log(parameter)
    $http.post(url, parameter).
      then(function(data, status, headers, config) {
        // this callback will be called asynchronously
        // when the response is available
        var key = "AIzaSyAvSqPeLkf4GVTiNrKaEl-S9Cb9FhCIX0Y"
        console.log(data);
        path = data.data;
        console.log(path);
        url = "https://maps.googleapis.com/maps/api/elevation/json?locations=".concat(path).concat("&key=").concat(key);
        console.log(url)
        $http.get(url).
          then(function successCallback(response) {
            $rootScope.routeJSON = response;
          }, function errorCallback(response){
            console.log("ERROR in callback");
            console.log(response);
          });
        //var Nightmare = require('nightmare');       
        //var nightmare = Nightmare({ show: true });
        //var gpsv = new Nightmare({
        //  waitTimeout: 5000
        //})
        //.viewport(1000,1000)
        //.useragent("Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36")
        //.goto("http://www.gpsvisualizer.com/convert_input")
        //.wait()
        //.screenshot('homepage.png');
      },
      function(data, status, headers, config) {
        // called asynchronously if an error occurs
        // or server returns response with an error status.
      });
		//console.log(e.route); // Logs the current route shown in the interface.
	});

	//change rider figure to zoom level
	map.on('zoomend', function() {
		var currentZoom = map.getZoom();
		var size = 45*currentZoom/18 + "px"
		rider._element.style.backgroundSize = size + " " + size;
		rider._element.style.width = size;
		rider._element.style.height = size;
	});

//  To edit the input boxes
//	document.getElementById("mapbox-directions-origin-input").children[0].children[1].value="TEST"
//	mapbox-directions-destination-input
//	mapbox-directions-origin-input
}	

