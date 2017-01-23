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
  var app = angular.module("renaBike", ["ngRoute", "highcharts-ng"]);
  
  app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix(''); //http://stackoverflow.com/questions/41214312/exclamation-mark-after-hash-in-angularjs-app/41551864#41551864
    $routeProvider
    .when("/", {templateUrl: "map.html", controller: "mapCtrl"})
    .when("/statistics", {templateUrl: "statistics.html", controller: "statCtrl"})
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
  });

  app.controller("weatherCtrl", function($scope, $http){
    closeNav();
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
