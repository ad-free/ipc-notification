# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..users.models import Customer
from ..schedule.models import Schedule
from ..notifications.models import GCM, APNS

from ..apis.utils import APIAccessPermission, update_or_create_device
from ..commons.utils import logger_format

from functools import partial

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
		result = update_or_create_device(APNS, name, device_token, username, new_username, password, False)
	elif platform == 'fcm':
		result = update_or_create_device(GCM, name, device_token, username, new_username, password, True)

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
	username = request.POST.get('username', '').strip()
	serial = request.POST.get('serial', '').strip()
	schedule_uuid = request.POST.get('schedule_uuid', '').strip()
	start_time = request.POST.get('start_time', '').strip()
	end_time = request.POST.get('end_time', '').strip()
	date = request.POST.get('date', '').strip()
	repeat_status = request.POST.get('repeat_status', '').strip()
	is_active = request.POST.get('is_active', 0)
	is_delete = request.POST.get('is_delete', 0)

	try:
		user = Customer.objects.get(username=username)
	except Customer.DoesNotExist:
		errors.update({'message': _('User does not exists.')})
	else:
		if int(is_delete) == 0:
			data_default = {
				'start_time': start_time,
				'end_time': end_time,
				'repeat_status': repeat_status,
				'is_active': True if int(is_active) == 1 else False
			}
			if int(repeat_status) == 0:
				data_default.update({'date': date, 'repeat_at': None})
			else:
				data_default.update({'date': None, 'repeat_at': date})
			obj_schedule, schedule_created = Schedule.objects.update_or_create(serial=serial, schedule_uuid=schedule_uuid, defaults=data_default)
			obj_schedule.user.add(user)
			message = _('Update your schedule successfully.')
		else:
			obj_schedule = Schedule.objects.get(serial=serial, schedule_uuid=schedule_uuid)
			obj_schedule.user.remove(user)
			message = _('You have successfully deleted the notification.')

		logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': message
		}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_delete'),))
def api_notification_delete(request):
	errors = {}
	serial = request.POST.get('serial', '').strip()
	schedule_uuid = request.POST.get('schedule_uuid', '').strip()

	try:
		obj_schedule = Schedule.objects.get(serial=serial, schedule_uuid=schedule_uuid)
		obj_schedule.delete()
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': _('You have successfully deleted the notification.')
		}, status=status.HTTP_200_OK)
	except Schedule.DoesNotExist:
		errors.update({'message': _('Schedule does not exists.')})

	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
