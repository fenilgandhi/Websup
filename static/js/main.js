'use strict';

// Initializes Websup Api
function Websup() {
	// Shortcuts to DOM Elements.
 	this.connection_status_btn = document.getElementById('connection_status_btn');
  this.send_message_btn = document.getElementById('send_message_btn');
  this.connected = false;
  this.messaging_queue = new Queue();
}


/* Send a login request to website */
Websup.prototype.connect = function() {
  $.ajax({
    url: "/api/login",
    type: "get",
    async : 'true',
  });
}

/* Checks if the site is still connected to yowsup */
Websup.prototype.check_connected = function() {
  $.ajax({
    url: "/api/connection_status",
    type: "get",
    async : 'false',
    timeout : 2000,
    success: function(response){
        if (response == "True") {
          $(websup.send_message_btn).removeClass('hidden');          
          websup.connection_status_btn.textContent = "Connected";
          websup.connected = true;
          console.log("Connected");
        }
        else{
          websup.connected = false;
          $(websup.send_message_btn).addClass('hidden');
          websup.connection_status_btn.textContent = "Not Connected" ;
          websup.connect();
          console.log("Disconnected");
          setTimeout(websup.check_connected, 5000);
        }
    },
  });
}

Websup.prototype.addelements = function() {
  while (websup.messaging_queue.getLength() < 10){
    var element = $('tbody tr')[0];
    if (element == undefined) { return;}
    var id = element.children[1].textContent;
    $.ajax({
        type:"GET",
        url:"/api/send/",
        timeout:2000,
        async : false,
        data: {
              'id': id,
        },
        success: function(response){
          if (response == "True"){
            websup.messaging_queue.push(id,element);
            $(element).appendTo('tfoot');
            element.children[0].textContent = "Added for Processing" ;
            console.log("Element Added");
          }
        }, 
      });
  }

}


Websup.prototype.message_manager = function() {
  websup.send_message_btn.onclick = function(){};
  websup.check_connected();

  if (websup.connected) {
    // Add Some Messages for processing
    websup.addelements();

    // Process the queue and remove successful elements
    var list = websup.messaging_queue.print();
    var i = 0;
    for(i in list){
      console.log(i);
      $.ajax({
        type:"GET",
        url:"/api/status/",
        timeout:2000,
        async : false,
        data: {
              'id': i,
        },
        success: function(response){
          if (response == "True"){
            var element = websup.messaging_queue.pop(i);
            element.children[0].textContent = "Sent";
            $(element).fadeOut(2000 , function() { $(element).remove() });
          }
        }, 
      });
    }
  }
  setTimeout(websup.message_manager, 6000);
}

$(document).ready( function() {
  window.websup = new Websup();
  websup.check_connected();
});