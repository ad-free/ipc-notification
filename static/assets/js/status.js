(function ($) {
	'use strict';

	$(document).ready(function () {
		try {
			var server = $('.server-info');
			var host = server.attr('data-host');
			var port = server.attr('data-port');
			var topic = server.attr('data-topic').replace('{name}', '+');
			__init__(host, port, topic);
		} catch (e) {
		}
	});

	function uuid(type) {
		function s4() {
			return Math.floor((1 + Math.random()) * 0x10000)
				.toString(16)
				.substring(1);
		}

		switch (type) {
			case 'hex':
				return s4() + s4() + s4() + s4() + s4() + s4() + s4() + s4();
			case 'normal':
				return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
		}
	}


	// called when the client connects
	function __init__(host, port, topic) {
		// Once a connection has been made, make a subscription and send a message.
		var tmp_timeout;
		try {
			if (tmp_timeout) {
				clearTimeout(tmp_timeout);
			}
			var clientID = 'iot-' + uuid('hex');
			var client = new Paho.MQTT.Client(host, Number(port), clientID);
			var options = {
				useSSL: false,
				timeout: 60,
				userName: 'notify',
				password: 'abcd@123456',
				cleanSession: true,
				onSuccess: function () {
					client.subscribe(topic);
				},
				onFailure: doFail
			};
			client.onConnectionLost = onConnectionLost;
			client.onMessageArrived = onMessageArrived;
			client.connect(options);
		} catch (e) {
			setTimeout(function () {
				__init__(host, port);
			}, 10000);
		}
	}

	// called when the client loses its connection
	function onConnectionLost(responseObject) {
		if (responseObject.errorCode !== 0) {
			console.log('onConnectionLost:' + responseObject.errorMessage);
		}
	}

	// called when a message arrives
	function onMessageArrived(message) {
		var data = JSON.parse(message.payloadString);

		if (data.hasOwnProperty('status')) {
			var topics = message.destinationName.split('/')[1];

			$('.field-username').each(function () {
				var name = $(this).find('a').text();

				if (name === topics) {
					if (data['status'] === 'online') {
						$(this).parent().find('.field-is_online > img').attr('src', '/static/admin/img/icon-yes.svg');
					} else {
						$(this).parent().find('.field-is_online > img').attr('src', '/static/admin/img/icon-no.svg');
					}
				}
			});
		}
	}

	// Connect failed
	function doFail(message) {
		alert(message.errorMessage);
	}
})(django.jQuery);