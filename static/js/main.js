'use strict';

// Initializes Websup Api
function Websup() {
	// Shortcuts to DOM Elements.
 	this.connection_status_btn = document.getElementById('connection_status_btn');

}

Websup.prototype.check_connected = function() {
	$.ajax({
    url: "/api/status",
    type: "get",
    async : 'true',
    success: function(response) {
        if (response == "True") {
          websup.connection_status_btn.textContent = "Connected";
        }
        else{
          websup.connection_status_btn.textContent = "Not Connected" ;
        }
    },
  });
}


Websup.prototype.send_message = function(element) {
  var id = element.children[1].textContent;
  $.ajax({
     type:"GET",
     url:"/api/send/",
     data: {
            'id': id,
     },
     success: function(response){
        if (response == "True") {
          element.children[0].textContent = "Sent";
        }
     }
  });
}

Websup.prototype.message_manager = function() {
  var rows = $('tr');
  for(var i=1; i<rows.length; i++) {
    websup.send_message( rows[i] );
  }
}

$(document).ready( function() {
  window.websup = new Websup();
  websup.check_connected();
  websup.connection_status_btn.onclick = websup.message_manager;
});