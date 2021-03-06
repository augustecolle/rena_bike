//VARIABLES
//var rider;
//var map;

function mapbox($http, $rootScope, $sce, $interval){
  mapboxgl.accessToken = 'pk.eyJ1IjoiYXVndXN0ZWNvbGxlIiwiYSI6ImNpeHE5b2p3YjAwMjgzM3AxYW11YTdqcm8ifQ.rWupKvdQ1UV6q4xJCBGKUw';

  var pos;
  map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/outdoors-v9',
    zoom: 18,
    center: [3.7174, 51.0543]
  });

  $rootScope.map = map;

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
     var options = {
        enableHighAccuracy: true,
        timeout: 60000,
          maximumAge: 0
    };
    if (navigator.geolocation) {
      
      navigator.geolocation.getCurrentPosition(function(position) {
        pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        rider = labelCurrentPosition(position.coords.latitude, position.coords.longitude);
        map.setCenter([pos.lng, pos.lat]);
        $rootScope.latitude = position.coords.latitude;
        $rootScope.longitude = position.coords.longitude;
        var callb = function(){
          var urlll = "https://"+location.hostname+":5000/Position";
          var parameter = {
            "gps_timestamp" : Date.now(),
            "gps_lat" : position.coords.latitude,
            "gps_lng" : position.coords.longitude,
            "gps_alt" : position.coords.altitude,
            "gps_pos_acc" : position.coords.accuracy,
            "gps_alt_acc" : position.coords.altitudeAccuracy,
            "gps_speed" : position.coords.speed,
            "gps_heading" : position.coords.heading
          };
          console.log(parameter);
          $http.post(urlll, parameter).
            then(function(data, status, headers, config) {
              //console.log("posted postion");
            }, function(data, status, headers, config) {
                console.log("Error");
            });
        };
        $rootScope.getWeather(callb);
        //$rootScope.startWeatherWatch(1); //weather get interval in minutes
        
      }, function(error){
        console.log("Error loading position: " + error);
        console.log(error);
      }, {enableHighAccuracy: true, timeout:60000});

      startPositionWatch = function(){
        urll = "https://"+location.hostname+":5000/Position";
        $rootScope.positionIndicator = navigator.geolocation.watchPosition(function(position) {
        var parameter = {
          "gps_timestamp" : Date.now(),
          "gps_lat" : position.coords.latitude,
          "gps_lng" : position.coords.longitude,
          "gps_alt" : position.coords.altitude,
          "gps_pos_acc" : position.coords.accuracy,
          "gps_alt_acc" : position.coords.altitudeAccuracy,
          "gps_speed" : position.coords.speed,
          "gps_heading" : position.coords.heading
        };
        $http.post(urll, parameter).
          then(function(data, status, headers, config) {
            //console.log("posted postion");
          }, function(data, status, headers, config) {
            alert('Failed to post position, maybe flask server is down?');
            console.log("Error");
          });
          rider.setLngLat([position.coords.longitude, position.coords.latitude]);
          $rootScope.latitude = position.coords.latitude;
          $rootScope.longitude = position.coords.longitude;
          $rootScope.accuracy = position.coords.accuracy; //in meters
          map.setCenter([position.coords.longitude, position.coords.latitude]);
          //console.log($rootScope.accuracy);

        }, function(error){
          console.log("Error loading position: " + error);
        }, options);
      }
    } else {
      alert("No geolocation supported");
    }
    var geolocate = new mapboxgl.GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true,
        watchPosition: true
      }
    });
    //geolocate.on('geolocate', function(e){
    //  console.log(e);
    //});
    map.addControl(directions);
    map.addControl(geolocate, 'bottom-right');
  });

  directions.on('route', function(e) {
    startPositionWatch();
    var parameter = e.route;
    url = "https://"+location.hostname+":5000/Trajectory"
    //console.log(parameter)
    $http.post(url, parameter).
      then(function(data, status, headers, config) {
        // this callback will be called asynchronously
        // when the response is available
        $rootScope.routeLats = [];
        $rootScope.routeLongs = [];
        $rootScope.cycletimes = [];
        $rootScope.cycletimescum = [];
        $rootScope.bearingsFromMapbox = [];
        for (var i = 0; i < data.data.length; i++){
          $rootScope.routeLats.push(data.data[i].lat);
          $rootScope.routeLongs.push(data.data[i].lng);
          $rootScope.cycletimes.push(data.data[i].cycletimes);
          $rootScope.cycletimescum.push(data.data[i].cycletimescum);
          $rootScope.bearingsFromMapbox.push(data.data[i].bearingsFromMapbox);
          //$rootScope.heading.push(data.data[i].heading);
          //$rootScope.distances.push(data.data[i].distances);
        }
        path = data.data;
        var elevator = new google.maps.ElevationService;
        elevator.getElevationForLocations({
            'locations': path
          }, getElevations);
        function getElevations(elevations, status){
          $rootScope.routeHeights = [];
          for (var i = 0; i < elevations.length; i++){
            $rootScope.routeHeights.push(elevations[i].elevation);
          }
          url = "https://"+location.hostname+":5000/Energy"
          var param = {"lats" : $rootScope.routeLats,
                       "lngs" : $rootScope.routeLongs,
                       "heights" : $rootScope.routeHeights,
                       "cycletimes" : $rootScope.cycletimes,
                       "weather" : $rootScope.weather["hourly_forecast"],
                       "bearingsFromMapbox": $rootScope.bearingsFromMapbox,
                       "newRoute":1
                      };
          $http.post(url, param).
            then(function(data, status, headers, config){
              //console.log("Success");
              $rootScope.energies = JSON.parse(data.data);
              //console.log("ENERGIES");
              //console.log($rootScope.energies);
            }, function(data, status, headers, config) {
              console.log("Error");
            });
        }
      },
      function(data, status, headers, config) {
        console.log("ENERGIE ERROR");
        // called asynchronously if an error occurs
        // or server returns response with an error status.
      });
		//console.log(e.route); // Logs the current route shown in the interface.

    var updateEnergies = function(){
      var url = "https://"+location.hostname+":5000/Energy";
      var param = {"lats" : $rootScope.routeLats,
                   "lngs" : $rootScope.routeLongs,
                   "heights" : $rootScope.routeHeights,
                   "cycletimes" : $rootScope.cycletimes,
                   "weather" : $rootScope.weather["hourly_forecast"],
                   "bearingsFromMapbox": $rootScope.bearingsFromMapbox,
                   "newRoute": 0
                  };
      $http.post(url, param).
        then(function(data, status, headers, config){
          //console.log("Success");
          $rootScope.energies = JSON.parse(data.data);
          //console.log("ENERGIES");
          //console.log($rootScope.energies);
        }, function(data, status, headers, config) {
          console.log("Error");
      });
  };
  var clearPosWatch = function(){
    //poll if the destination is reached
    url = "https://"+location.hostname+":5000/Position"
    $http.get(url).
      then(function(data, status, headers, config){
        console.log(data.data);
        if (data.data){
          navigator.geolocation.clearWatch($rootScope.positionIndicator);
          console.log("REACHED DESTINATION")
          $rootScope.routed_flag = 0;
        }
      }, function(data, status, headers, config) {
        console.log("Error in get position");
      });
  };

  if ($rootScope.routed_flag == 1){
    console.log("Already routing");
  } else {
    $interval(updateEnergies, 1000*60*5); //recalculate energies every 5 minutes (in [ms])
    $interval(clearPosWatch, 1000*5); //check every 5 seconds if destination is reached
    $rootScope.routed_flag = 1;
  };
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

