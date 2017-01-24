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
  var app = angular.module("renaBike", ["ngRoute", "highcharts-ng"])
    .run(function($rootScope){
      $rootScope.pos = {};
   });

  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
    .when("/weather", {templateUrl: "weather.html", controller: "weatherCtrl"});
    //.otherwise({redirectTo: "/map"});    
  });
  
  app.controller("mapCtrl", function($rootScope, $scope){
    closeNav();
    autoResizeDiv();
    $rootScope.pos = mapbox();
    console.log("JA")
    console.log($rootScope.pos);
  });
  
  app.controller("statCtrl", function($scope){
    closeNav();
    $scope.tabs = [true, false, false];

    $scope.chart1Config = {
      chart: {
        type: 'line'
      },
      xAxis: {
        categories: jsonTemp["position"]
      },
      series: jsonTemp["energy"],
      title: {
        text: 'Hello'
      }
    }

    $scope.clickTab = function(number){
      $scope.tabs = [false, false, false];
      $scope.tabs[number] = true;
      //tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
    }
  });

  app.controller("weatherCtrl", function($rootScope, $scope, $http){
    closeNav();
    $scope.response = "Eerst";
    $scope.getData = $http.get("https://"+location.hostname+":5000/Weather", {params: {'lat':12, 'long':52}})
        .then(function(response) {
          console.log(response);
          console.log($rootScope.pos);
          $scope.response = response.data;
    });
  });
})();
