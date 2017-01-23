(function(){
  var app = angular.module("renaBike", ["ngRoute"]);
  
  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
    //.when("/dashboard", {templateUrl: "statistics.html", controller: "statCtrl"});
    .when("/weather", {templateUrl: "weather.html", controller: "weatherCtrl"});
    //.otherwise({redirectTo: "/map"});    
  });
  
  app.controller("mapCtrl", function($scope){
    closeNav();
    autoResizeDiv();
    mapbox();
  });
  
  app.controller("statCtrl", function($scope){
    closeNav();
    $scope.tabs = [true, false, false];
    
    $scope.clickTab = function(number){
      $scope.tabs = [false, false, false];
      $scope.tabs[number] = true;
      //tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
    }
  });

  app.controller("weatherCtrl", function($scope, $http){
    $scope.getData = function(){
      console.log("JAAAAA");
      $http.get("https://"+location.hostname+":5000/Weather")
        .success(function(response) {
          console.log(response);
          $scope.response = response;
      });
    }
  });
  
})();
