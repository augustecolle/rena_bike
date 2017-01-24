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
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
    .when("/weather", {templateUrl: "weather.html", controller: "weatherCtrl"});
    //.otherwise({redirectTo: "/map"});    
  });
  
  app.controller("mapCtrl", function($rootScope, $scope, $geolocation){
    closeNav();
    autoResizeDiv();
    mapbox();
    //$geolocation.watchPosition({
    //  timeout: 60000,
    //  maximumAge: 250,
    //  enableHighAccuracy: true
    //});
    //$rootScope.myPosition = $geolocation.position;
    //console.log($rootScope.myPosition);
  });
  
  app.controller('geolocCtrl', ['$geolocation', '$scope', function($geolocation, $scope, $rootScope) {
    $geolocation.watchPosition({
       timeout: 60000,
       maximumAge: 250,
       enableHighAccuracy: true
    });
    $rootScope.myPosition = $geolocation.position;
    console.log($rootScope.myPosition);
  }]);

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
    $scope.response = "Eerst";
    $scope.getData = $http.get("https://"+location.hostname+":5000/Weather", {params: $rootScope.myPosition})
        .then(function(response) {
          $scope.response = response.data;
          console.log($rootScope.myPosition);
    }, function errorCallback(response){
      console.log("ERROR, did you initialize the flask server??");  
      console.log($rootScope.myPosition);
    });
  });
})();
