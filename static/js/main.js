'use strict';

// Initializes Websup Api
function Websup() {
	// Shortcuts to DOM Elements.
 	this.connection_status_btn = document.getElementById('connection_status_btn');
  this.send_message_btn = document.getElementById('send_message_btn');
}

Websup.prototype.connect = function() {
  $.ajax({
    url: "/api/login",
    type: "get",
    async : 'true',
  });
}

Websup.prototype.check_connected = function() {
  $.ajax({
    url: "/api/connection_status",
    type: "get",
    async : 'true',
    success: function(response){
        if (response == "True") {
          $(websup.send_message_btn).removeClass('hidden');          
          websup.connection_status_btn.textContent = "Connected";
        }
        else{
          $(websup.send_message_btn).addClass('hidden');
          websup.connection_status_btn.textContent = "Not Connected" ;
          websup.connect();
        }
    },
  });
}

Websup.prototype.send_messages = function(){
  
  var element = $('tbody tr')[0];
  if (element == undefined) { return; }
  var id = element.children[1].textContent;
  console.log(id);
  var x = $(element);
  x.appendTo( $('tfoot') );
  $.ajax({
     type:"GET",
     url:"/api/send/",
     timeout:5000,
     data: {
            'id': id,
     },
     success: function(response){
        if (response == "True"){
          element.children[0].textContent = "Sent";
          x.fadeOut(2000 , function() { x.remove() });
          websup.send_messages();
        }
     },
     error: function(){
      x.addClass('text-danger');
      websup.send_messages();
     }

  });
}

Websup.prototype.message_manager = function() {
  websup.send_messages();
}

$(document).ready( function() {
  window.websup = new Websup();
  websup.check_connected();
  setInterval(websup.check_connected , 5000);
});