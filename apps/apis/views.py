# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.contrib.auth.models import User
from ..schedule.models import Schedule
from push_notifications.models import GCMDevice, APNSDevice

from ..apis.utils import APIAccessPermission, update_or_create_device
from ..commons.utils import logger_format

from functools import partial
from ast import literal_eval

import logging

logger = logging.getLogger('')


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_register'),))
def api_notification_register(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_register.__name__))
	errors = {}
	result = ''
	username = request.POST.get('username', '').strip()
	new_username = request.POST.get('new_username', '').strip()
	password = request.POST.get('password', '')
	platform = request.POST.get('platform', '').strip()
	device_token = request.POST.get('device_token', '').strip()
	bundle = request.POST.get('bundle', '').strip()
	name = platform + '_' + bundle

	logger.info(logger_format('Check your platform', api_notification_register.__name__))
	if platform == 'apns':
		result = update_or_create_device(APNSDevice, name, device_token, username, new_username, password, False)
	elif platform == 'fcm':
		result = update_or_create_device(GCMDevice, name, device_token, username, new_username, password, True)

	if result:
		logger.info(logger_format('<-------  END  ------->', api_notification_register.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': _('You have successfully registered.')
		}, status=status.HTTP_200_OK)
	else:
		errors.update({'message': _('New username always exists.')})
		logger.error(logger_format('New username always exists.', api_notification_register.__name__))

	logger.info(logger_format('<-------  END  ------->', api_notification_register.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors if errors else _('Check your platform and bundle fields.')
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_update'),))
def api_notification_update(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_update.__name__))
	errors = {}
	message = ''
	username = request.POST.get('username', '').strip()
	serial = request.POST.get('serial', '').strip()
	schedule = literal_eval(request.POST.get('schedule', '').strip())
	is_active = request.POST.get('is_active', '').strip()

	logger.info(logger_format('Check is_active', api_notification_update.__name__))
	if int(is_active) == 1:
		is_active = True
	else:
		is_active = False

	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		errors.update({'message': _('User does not exists.')})
	else:
		obj_schedule, schedule_created = Schedule.objects.update_or_create(
				user=user.username,
				serial=serial,
				defaults={'schedule': schedule, 'is_active': is_active}
		)
		logger.info(logger_format('Check schedule', api_notification_update.__name__))
		if obj_schedule:
			logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
			return Response({
				'status': status.HTTP_200_OK,
				'result': True,
				'message': _('Update your schedule successfully.') if not message else message
			}, status=status.HTTP_200_OK)
		else:
			errors.update({'message': _('Update your schedule unsuccessful.')})

	logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_push'),))
def api_notification_push(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_push.__name__))
	errors = {}
	serial = request.POST.get('serial', '').strip()

	try:
		obj_schedule = Schedule.objects.get(serial=serial)
		obj_user = User.objects.get(username=obj_schedule.user)
	except Schedule.DoesNotExist:
		errors.update({'message': _('Schedule does not exists.')})
	except User.DoesNotExist:
		errors.update({'message': _('User does not exists.')})
	else:
		APNSDevice.objects.filter(user=obj_user)
		GCMDevice.objects.filter(user=obj_user)

	logger.info(logger_format('<-------  END  ------->', api_notification_push.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
