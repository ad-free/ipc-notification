# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.utils.dateformat import format
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions

from .models import Registration
from ..users.models import Customer
from push_notifications.models import CLOUD_MESSAGE_TYPES

from datetime import datetime, timedelta

import logging

logger = logging.getLogger('')


def update_or_create_device(device, name, token, username, password, android=False):
	obj_user, user_created = Customer.objects.get_or_create(username=username)
	if obj_user:
		# noinspection PyBroadException
		try:
			obj_user.password = make_password(password)
			obj_user.save()
		except Exception:
			pass
		else:
			obj_device, device_created = device.objects.get_or_create(name=name, user=obj_user)
			if android:
				obj_device.cloud_message_type = CLOUD_MESSAGE_TYPES[0][0]
			obj_device.registration_id = token
			obj_device.save()
			return True
	return False


def message_format(title='', body='', url='', acm_id='', time='', serial=''):
	return {
		'title': title,
		'body': body,
		'url': url,
		'acm_id': acm_id,
		'time': time,
		'camera_serial': serial
	}


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
