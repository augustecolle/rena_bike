(function(){
  var app = angular.module("renaBike", ["ngRoute"]);

  app.config(function($routeProvider) {
    $routeProvider.when('/', {templateUrl: 'map.html', controller: 'map'});
    $routeProvider.when('/map', {templateUrl: 'map.html', controller: 'map'}); 
    $routeProvider.when('/statistics', {templateUrl: 'statistics.html'}); 
    //$routeProvider.when('/location/:id/:from?/:fromID?', {templateUrl: 'places.html', reloadOnSearch: false});
  });
  
  app.controller("map", function($scope){
    autoResizeDiv();
    mapbox();
  });
  
})();