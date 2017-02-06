
function getAbsoluteHeight(el) {
  // Get the DOM Node if you pass in a string
  el = (typeof el === 'string') ? document.querySelector(el) : el;
  var styles = window.getComputedStyle(el);
  var margin = parseFloat(styles['marginTop']) +
               parseFloat(styles['marginBottom']);
  return Math.ceil(el.offsetHeight + margin) + 1;
}

//if(navigator.userAgent.indexOf("Firefox")<0) alert("Only Firefox is supported!");

function autoResizeDiv($rootScope){
  console.log("resizing");
  if (document.getElementById("mapAng")) {
    document.getElementById("mapAng").style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
    console.log("resized mapAng");
  } else if (document.getElementById("graph1")) {
    
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
    y = y - document.getElementById('header').offsetHeight - getAbsoluteHeight(document.getElementById('tabHeadStatistics'));

    $rootScope.chart1Config = new Highcharts.Chart({
      chart: {
        renderTo: 'graph1',
        type: 'line',
        zoomType: 'xy',
        animation: true,
        width: x,
        height: y
      },
      xAxis: {
        categories: $rootScope.energies["position"],
        tickmarkPlacement: 'on',
        labels: {
          format: "{value:.2f} km"
        },
        title: {
         text: "Distance [km]" 
        }
      },
      yAxis: {
        title: {
          text: "Energy [Wh]"
        }
      },
      series: $rootScope.energies["energy"],
      title: {
        text: "Energy usage"
      },
      tooltip: {
        formatter: function(){
          return "Distance: " +this.x + " km <br\> " + this.series.name + ": " + this.y + " Wh"
        }
      }
    });
    $rootScope.$broadcast('highchartsng.reflow');
    document.getElementById("graph1").style.height = y + 'px';
//    var w = window,
//        d = document,
//        e = d.documentElement,
//        g = d.getElementsByTagName('body')[0],
//        x = w.innerWidth || e.clientWidth || g.clientWidth,
//        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
//    y = y - document.getElementById('header').offsetHeight - getAbsoluteHeight(document.getElementById('tabHeadStatistics'));
//    $rootScope.hsWidth = x;
//    $rootScope.hsHeight = y;
//    console.log($rootScope);
    console.log("resized chart");

  } else if (document.getElementById("map")) {
  console.log("map resized");
    document.getElementById('map').style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
    console.log("resized map");
  } else {
    console.log("nothing to resize");
  }
}

function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  //document.getElementById("main").style.backgroundColor = "rgba(0,0,0,0.4)";
};
		
/* Set the width of the side navigation to 0 and the left margin of the page content to 0, and the background color of body to white */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  //document.getElementById("main").style.backgroundColor = "white";
};




