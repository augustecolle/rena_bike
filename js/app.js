(function(){
  var app = angular.module("renaBike", ["ngRoute", "highcharts-ng", "ngGeolocation"])

  app.run(function($rootScope, $http, $sce, $interval) {
    $rootScope.latitude = 0;
    $rootScope.longitude = 0;
    $rootScope.accuracy = 0;
    $rootScope.routeLats = [];
    $rootScope.routeLongs = [];
    $rootScope.routeHeights = [];
    $rootScope.cycletimes = [];
    $rootScope.cycletimescum = [];
    $rootScope.energies = {};
    $rootScope.weather = {};
    $rootScope.treated_weather = {};
    $rootScope.bearingsFromMapbox = [];
    $rootScope.hidden = 0;
    $rootScope.routed_flag = 0;
    $rootScope.tabs = [false, false, false, false];
    //var updateScreen = function(){
    //  autoResizeDiv($rootScope);
    //};
    //$interval(updateScreen, 1000);
    autoResizeDiv($rootScope);
    mapbox($http, $rootScope, $sce, $interval);
    window.onresize = function(){
      //autoResizeDiv($rootScope);
    }

    $rootScope.getWeather = function(callb) {
      apikey = "2b26e3479da80130";
      $http({method: "GET", url: "https://api.wunderground.com/api/" + apikey + "/hourly10day/q/" + $rootScope.latitude + "," + $rootScope.longitude + ".json"})
        .then(function successCallback(response) {
          $rootScope.weather = response["data"];
          //console.log(location.hostname);
          //console.log(response);
          var url = "https://"+location.hostname+":5000/Weather"
          $http.post(url, $rootScope.weather).
            then(function(data, status, headers, config) {
              $http.get("https://"+location.hostname+":5000/Weather").
                then(function(response) {
                  $rootScope.treated_weather = response.data;
                  callb();
                  //console.log(response.data);
                  //console.log("Treated data");
                }, function errorCallback(response){
                  console.log("Error on treating data");  
                });
              //console.log("Wheater post");
            }, function(data, status, headers, config) {
              console.log("weather error");
            });
          }, function errorCallback(response) {
          alert("Weather isn't available");
      });
    }
    
    $rootScope.startWeatherWatch = function(intervalTime) { //intervalTime in minutes
      intervalTime = intervalTime * 60 * 1000;
      $rootScope.weatherInterval = $interval(function() {
        $rootScope.getWeather();
      }, intervalTime);
    };
    
  });

  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    //.when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/map", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
    //.when("/weather", {templateUrl: "weather.html", controller: "weatherCtrl"});
    .when("/settings", {templateUrl: "settings.html", controller: "settingsCtrl"});
    //.otherwise({redirectTo: "/map"});    
  }, function($sceProvider){
    $sceProvider.enabled(false);
  });
/*
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
  ]);*/

  //app.controller("rootCtrl", ['$geolocation','$scope', function($geolocation, $scope, $http){
  app.controller("rootCtrl", function($geolocation, $scope, $rootScope, $http){

  });

  app.controller("mapCtrl", function($rootScope, $scope, $geolocation, $http, $sce){
    $rootScope.hidden = 0;
    $rootScope.tabs = [false, false, false, false];
    //closeNav();
    autoResizeDiv($rootScope);
  });

  app.controller("statCtrl", function($scope, $rootScope){
    //closeNav();
    $rootScope.hidden = 1;
    $scope.tabs = [true, false, false, false];
    $rootScope.tabs = [true, false, false, false];
    autoResizeDiv($rootScope);

    $scope.clickTab = function(number){
    $scope.tabs = [false, false, false, false];
    $scope.tabs[number] = true;
    $rootScope.tabs = [false, false, false, false];
    $rootScope.tabs[number] = true;
    //highlight the selection
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" w3-dark-grey", "");
    }
    tablinks[number].className += (" w3-dark-grey");
    autoResizeDiv($rootScope);
  }
  });


  app.controller("weatherCtrl", function($rootScope, $scope, $http){
    //closeNav();
    $rootScope.hidden = 1;
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
  

  app.controller("settingsCtrl", function($rootScope, $scope, $http){
    //closeNav();
    //
    $scope.request_users = function(){
      $http.get("https://"+location.hostname+":5000/Settings")
          .then(function(response) {
            $scope.userdata = JSON.parse(response.data);
            //console.log($scope.userdata);
            $scope.update();
      }, function errorCallback(response){
        console.log("ERROR in settings request, did you initialize the flask server??");
      });
    };
 
    $scope.request_lastID = function(){
      $http.get("https://"+location.hostname+":5000/globalSettings")
          .then(function(response) {
            $scope.selectedID = response.data;
            $scope.request_users();
      }, function errorCallback(response){
        console.log("ERROR in global settings request, did you initialize the flask server??");
      });
    }

    $scope.update = function(){
      $rootScope.ID = $scope.selectedID;
      $scope.ID = $rootScope.ID;
      $scope.name = $scope.userdata[$rootScope.ID].name;
      $scope.weight = $scope.userdata[$rootScope.ID].weight;
      $scope.length = $scope.userdata[$rootScope.ID].length;
      $scope.crr = $scope.userdata[$rootScope.ID].cr;
      $scope.cr = $scope.userdata[$rootScope.ID].cr;
      $scope.cdaa = $scope.userdata[$rootScope.ID].cda;
      $scope.cda = $scope.userdata[$rootScope.ID].cda;
      $scope.v_cyclist = $scope.userdata[$rootScope.ID].v_cyclist;
      $scope.profileText = "Edit"
      $scope.editProfile = true;
      var url = "https://"+location.hostname+":5000/globalSettings";
      $http.post(url, $rootScope.ID).
        then(function(data, status, headers, config) {
          //console.log("posted settings");
        }, function(data, status, headers, config) {
          console.log("ERROR IN SENDING USER SETTINGS TO DB");
        });
    }

    //create new profile 
    $scope.newPr = function(){
      //console.log("new profile");
      $scope.name = null;
      $scope.profileText = "Edit";
      $scope.newProfile = true;
      $scope.weight = null;
      $scope.length = null;
      $scope.crr = null;
      $scope.cr = 0.01;
      $scope.cdaa = null;
      $scope.cda = 0.6;
      $scope.v_cyclist = null;
      $scope.ID = -1;
    }
   
    $scope.request_lastID();
    $rootScope.hidden = 1;
    $scope.newProfile = false;
    $scope.editProfile = false;
    $scope.profileText = "New"
   
    $scope.addProfile = function(){
      if(!$scope.newProfile){
        $scope.newProfile = true;
        $scope.profileText = "Hide"
      } else {
        $scope.newProfile = false;
        if (!$scope.editProfile){
          $scope.profileText = "New"
        } else {
          $scope.profileText = "Edit";
        }
      }
    };  

    //Check input values in the form before enabling save button
    $scope.checkForm = function(){
      if($scope.v_cyclist && $scope.length && $scope.weight && $scope.name){
        return true;
      } else {
        return false;
      };
    };
  
    $scope.save = function(){
      var url = "https://"+location.hostname+":5000/Settings"
      dict = {};
      dict[$scope.name] = [$scope.ID, $scope.weight, $scope.length, $scope.cr, $scope.cda, $scope.v_cyclist]
      $http.post(url, dict).
        then(function(data, status, headers, config) {
          //console.log("posted settings");
        }, function(data, status, headers, config) {
          console.log("ERROR IN SENDING USER SETTINGS TO DB");
        });
    };

  });
  
})();
