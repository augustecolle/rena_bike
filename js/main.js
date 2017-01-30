window.onresize = autoResizeDiv;

function autoResizeDiv(){
  if (document.getElementById("map")){
    document.getElementById("map").style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
  } else if (document.getElementById("mapAng")) {
    document.getElementById("mapAng").style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
  } else if (document.getElementById("statistics")) {
    document.getElementById('statistics').style.height = window.innerHeight - document.getElementById('header').offsetHeight + 'px';
  } else {
    console.log("nothing to resize");
  }
};

function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
};
		
/* Set the width of the side navigation to 0 and the left margin of the page content to 0, and the background color of body to white */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  document.body.style.backgroundColor = "white";
};




