# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.dateformat import format
from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions

from .models import Registration
from ..users.models import Customer
from push_notifications.models import CLOUD_MESSAGE_TYPES


from datetime import datetime, timedelta

import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import ssl
import json
import uuid
import logging

logger = logging.getLogger('')


def update_or_create_device(device, name, token, username, password, android=False):
	obj_user, user_created = Customer.objects.get_or_create(username=username)
	if obj_user:
		obj_user.password = make_password(password)
		# noinspection PyBroadException
		try:
			obj_user.save()
		except Exception:
			pass
		else:
			obj_device, device_created = device.objects.get_or_create(name=name, registration_id=token)
			if android:
				obj_device.cloud_message_type = CLOUD_MESSAGE_TYPES[0][0]
			obj_device.user = obj_user
			obj_device.is_active = True
			obj_device.save()
			return {'success': True, 'message': _('You have successfully updated.')}
	return {'success': False, 'message': _('Device token always exists.')}


def message_format(**kwargs):
	return {
		'title': kwargs['title'],
		'body': kwargs['body'],
		'url': kwargs['url'],
		'acm_id': kwargs['acm_id'],
		'time': kwargs['time'],
		'camera_serial': kwargs['camera_serial'],
		'letter_type': kwargs['letter_type'],
		'attachment': kwargs['attachment'],
		'notification_title': kwargs['notification_title'],
		'notification_body': kwargs['notification_body'],
		'notification_type': kwargs['notification_type']
	}


def single_subscribe_or_publish(topic, payload=None, qos=0, is_publish=False, is_subscribe=False):
	auth = {
		'username': settings.API_ALERT_USERNAME,
		'password': settings.API_ALERT_PASSWORD
	}
	tls = {
		'ca_certs': settings.CA_ROOT_CERT_FILE,
		'certfile': settings.CA_ROOT_CERT_CLIENT,
		'keyfile': settings.CA_ROOT_CERT_KEY,
		'cert_reqs': ssl.CERT_NONE,
		'tls_version': settings.CA_ROOT_TLS_VERSION,
		'ciphers': settings.CA_ROOT_CERT_CIPHERS
	}
	if is_publish:
		publish.single(
				topic=topic,
				payload=payload,
				qos=qos,
				retain=True,
				hostname=settings.API_QUEUE_HOST,
				port=settings.API_QUEUE_PORT,
				client_id='iot-{}'.format(uuid.uuid1().hex),
				auth=auth,
				tls=tls
		)
		return True
	if is_subscribe:
		message = subscribe.simple(
				topics=topic,
				hostname=settings.API_QUEUE_HOST,
				port=settings.API_QUEUE_PORT,
				client_id='iot-{}'.format(uuid.uuid1().hex),
				auth=auth,
				tls=tls
		)
		return message
	return False


def app_registration(app_id):
	app = Registration.objects.get(app_id=app_id, status=True)
	if app:
		features = list(app.features.values_list('name', flat=True))
		return {
			'app_package': app.app_package,
			'app_type': app.app_type,
			'server_status': app.server,
			'features': features
		}
	return None


class APIAccessPermission(permissions.BasePermission):
	message = _('Page was not found on this server.')

	def __init__(self, stack):
		self.stack = stack

	def has_permission(self, request, view):
		try:
			if 'HTTP_GIS' in request.META:
				app_id = request.META.get('HTTP_GIS', '')
				if len(app_id) > 0:
					if request.session.get(app_id, None) is None:
						app = app_registration(app_id)
						app.update({'session_created': int(format(datetime.now(), u'U'))})
						request.session[app_id] = app
					else:
						temp = request.session[app_id]
						time_ago = int(format(datetime.now() - timedelta(seconds=180), u'U'))
						if time_ago > int(temp['session_created']):
							app = app_registration(app_id)
							app.update({'session_created': int(format(datetime.now(), u'U'))})
							request.session[app_id] = app
						else:
							app = request.session[app_id]
					# Checking permission to access APIs
					if app:
						if app['app_type'] == 'web':
							if request.META['HTTP_HOST'] not in app['app_package']:
								return False
						else:
							if 'HTTP_PACKAGE' not in request.META:
								return False
							elif request.META['HTTP_PACKAGE'] not in app['app_package']:
								return False
						app_feature = self.stack
						if app_feature in app['features']:
							return True
		except Exception as e:
			logger.error('{}'.format(e))
			pass
		return False
