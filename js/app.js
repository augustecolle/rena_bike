jsonTemp = {
  "position": [
    10,
    20,
    30
  ],
  "energy": [
    {
      "name": "totaal",
      "data": [
        24,
        45,
        60
      ]
    },
    {
      "name": "rol",
      "data": [
        12,
        34,
        45
      ]
    }
  ],
  "altitude": [
    100,
    200,
    250
  ]
};

(function(){
  var app = angular.module("renaBike", ["ngRoute", "highcharts-ng", "ngGeolocation"])
    .run(function($rootScope, $geolocation){
      $rootScope.myPosition = {};
      //$geolocation.watchPosition({
      //  timeout: 60000,
      //  maximumAge: 250,
      //  enableHighAccuracy: true
      //});
      //$rootScope.myPosition = $geolocation.position;
      //console.log($rootScope.myPosition);
   });

  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    //.when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/map", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
    .when("/weather", {templateUrl: "weather.html", controller: "weatherCtrl"});
    //.otherwise({redirectTo: "/map"});    
  });

  app.directive('mapbox', [
    function () {
      return {
        restrict: 'A',
        replace: true,
        scope: {
        },
        link: function ($scope, $element, $attributes) {
          document.getElementById("mapAng").style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
          mapboxgl.accessToken = 'pk.eyJ1IjoiYXVndXN0ZWNvbGxlIiwiYSI6ImNpeHE5b2p3YjAwMjgzM3AxYW11YTdqcm8ifQ.rWupKvdQ1UV6q4xJCBGKUw';
          console.log($element[0]);
          var map = new mapboxgl.Map({
            container:$element[0],
	          style: 'mapbox://styles/mapbox/outdoors-v9',
	          zoom: 18,
	          center: [3.7174, 51.0543]
          });
        }
      };
    }
  ]);

  //app.controller("rootCtrl", ['$geolocation','$scope', function($geolocation, $scope, $http){
  app.controller("rootCtrl", function($geolocation, $scope, $rootScope, $http){
    //eenmalig ophalen tot de watcher start
    navigator.geolocation.getCurrentPosition(function(position) {
      pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      console.log(pos);
    });
    //Geo watcher
    $geolocation.watchPosition({
      timeout: 60000,
      maximumAge: 250,
      enableHighAccuracy: true
    });
    $rootScope.myPosition = $geolocation.position; // this object updates regularly, it has 'error' property which is a 'truthy' and also 'code' and 'message' property if an error occurs
    /*//It has all the location data 
    '$scope.myPosition.coords'
    //It's truthy and gets defined when error occurs 
    '$scope.myPosition.error'*/
    
    //Weahter
    apikey = "aab29414b85baab539aeac7451de4b45";
    //alert($scope.myPosition.coords)
    //$http({method: 'GET', url: 'http://api.openweathermap.org/data/2.5/forecast', params: {'lat': $scope.myPosition.coords.latitude, 'lon': $scope.myPosition.coords.longitude, 'APPID': apikey}})
    $http({method: 'GET', url: 'http://api.openweathermap.org/data/2.5/forecast', params: {'lat': 53, 'lon': 4, 'APPID': apikey}})
      .then(function successCallback(response) {
        weather = response["data"];
        console.log(weather);
      }, function errorCallback(response) {
        alert("Weather isn't available")
      });
  });
/*
  app.controller("mapAngCtrl", function($rootScope, $scope, $geolocation){
    closeNav();
    autoResizeDiv();
  });*/

  app.controller("mapCtrl", function($rootScope, $scope, $geolocation, $http){
    closeNav();
    autoResizeDiv();
    mapbox($http);
    /*navigator.geolocation.getCurrentPosition(function(position) {
		  	pos = {
		      lat: position.coords.latitude,
		      lng: position.coords.longitude
		    };
      console.log(pos);
    });*/
    //$geolocation.watchPosition({
    //  timeout: 60000,
    //  maximumAge: 250,
    //  enableHighAccuracy: true
    //});
    //$rootScope.myPosition = $geolocation.position;
    //console.log($rootScope.myPosition);
  });
  /*
  app.controller('geolocCtrl', ['$geolocation', '$scope', function($geolocation, $scope, $rootScope) {
    $geolocation.watchPosition({
       timeout: 60000,
       maximumAge: 250,
       enableHighAccuracy: true
    });
    $rootScope.myPosition = $geolocation.position;
    console.log($rootScope.myPosition);
  }]);*/

  app.controller("statCtrl", function($scope){
    closeNav();
    $scope.tabs = [true, false, false];

    $scope.chart1Config = {
      chart: {
        type: 'line',
        zoomType: 'xy',
        animation: false
      },
      xAxis: {
        categories: jsonTemp["position"],
        tickmarkPlacement: 'on',
        title: {
         text: "Distance [km]" 
        }
      },
      yAxis: {
        title: {
          text: "Energy [Wh]"
        }
      },
      series: jsonTemp["energy"],
      title: {
        text: "Energy usage"
      },
      tooltip: {
        formatter: function(){
          return "Distance: " +this.x + " km <br\> " + this.series.name + ": " + this.y + " Wh"
        }
      }
    }

    $scope.clickTab = function(number){
      $scope.tabs = [false, false, false];
      $scope.tabs[number] = true;
      //highlight the selection
      tablinks = document.getElementsByClassName("tablink");
      for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" w3-dark-grey", "");
      }
      tablinks[number].className += (" w3-dark-grey");
  }

  $scope.clickTab = function(number){
    $scope.tabs = [false, false, false];
    $scope.tabs[number] = true;
    //highlight the selection
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" w3-dark-grey", "");
    }
    tablinks[number].className += (" w3-dark-grey");
  }
  });

  app.controller("weatherCtrl", function($rootScope, $scope, $http){
    closeNav();
    /*$scope.response = "Eerst";
          $scope.position = $rootScope.myPosition;
    $scope.getData = $http.get("https://"+location.hostname+":5000/Weather", {params: {'lat':51, 'long':3}})
        .then(function(response) {
          $scope.response = response.data;
          console.log($rootScope.myPosition);
    }, function errorCallback(response){
      console.log("ERROR, did you initialize the flask server??");  
      console.log($rootScope.myPosition);
    });*/
  });
})();
