'use strict';

// Initializes Websup Api
function Websup() {
	// Shortcuts to DOM Elements.
 	this.connection_status_btn = document.getElementById('connection_status_btn');

}

Websup.prototype.check_connected = function() {
	var websup = this;
	$.ajax({
            url: "/api/status",
            type: "get",
            async : 'true',
            success: function(response) {
                websup.connection_status_btn.textContent = response;
            },
    });
}

$(document).ready( function() {
  window.websup = new Websup();
  websup.check_connected();
});