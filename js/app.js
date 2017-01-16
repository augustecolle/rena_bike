(function(){
  var app = angular.module("renaBike", ["ngRoute", "ui.bootstrap"]);
  
  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"});
    //.when("/dashboard", {templateUrl: "statistics.html", controller: "statCtrl"});
    //.when("/weather", {templateUrl: "statistics.html", controller: "statCtrl"});
    //.otherwise({redirectTo: "/map"});    
  });
  
  app.controller("mapCtrl", function($scope){
    closeNav();
    autoResizeDiv();
    mapbox();
  });
  
  app.controller("statCtrl", function($scope){
    closeNav();
    
  });
  
})();