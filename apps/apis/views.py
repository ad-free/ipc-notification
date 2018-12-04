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

import json
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
	schedule_id = request.POST.get('schedule_id', '').strip()
	start_time = request.POST.get('start_time', '').strip()
	end_time = request.POST.get('end_time', '').strip()
	date = request.POST.get('date', '').strip()
	repeat_status = request.POST.get('repeat_status', '').strip()
	is_active = request.POST.get('is_active', '0').strip()
	is_unshared = request.POST.get('is_unshared', '0').strip()

	try:
		user = Customer.objects.get(username=username)
	except Customer.DoesNotExist:
		logger.error(logger_format('User does not exists.', api_notification_update.__name__))
		errors.update({'message': _('User does not exists.')})
	else:
		if int(is_unshared) == 1:
			obj_schedule = Schedule.objects.filter(serial=serial)
			if obj_schedule.exists():
				for schedule in obj_schedule:
					schedule.user.remove(user)
		else:
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
			obj_schedule, schedule_created = Schedule.objects.update_or_create(serial=serial, schedule_id=schedule_id, defaults=data_default)
			if int(is_active) == 1:
				obj_schedule.user.add(user)
			else:
				obj_schedule.user.remove(user)
		logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': _('Update your schedule successfully.')
		}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_active'),))
def api_notification_active(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_active.__name__))
	errors = {}
	username = request.POST.get('username', '').strip()
	serial = request.POST.get('serial', '').strip()
	schedule_id = request.POST.get('schedule_id', '').strip()
	is_active = request.POST.get('is_active', '0').strip()

	logger.info(logger_format('Check serial', api_notification_active.__name__))
	if not serial:
		errors.update({'serial': _('This field is required.')})

	logger.info(logger_format('Check username', api_notification_active.__name__))
	if not username:
		errors.update({'username': _('This field is required.')})

	if not errors:
		try:
			user = Customer.objects.get(username=username)
		except Customer.DoesNotExist:
			logger.error(logger_format('User does not exists.', api_notification_active.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			if int(is_active) == 1:
				for schedule in json.loads(schedule_id):
					try:
						obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
						obj_schedule.user.add(user)
					except Schedule.DoesNotExist:
						logger.warning(logger_format('Schedule does not exists.', api_notification_active.__name__))
				message = _('Activate notification successful.')
			else:
				for schedule in json.loads(schedule_id):
					try:
						obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
						obj_schedule.user.remove(user)
					except Schedule.DoesNotExist:
						logger.warning(logger_format('Schedule does not exists.', api_notification_active.__name__))
				message = _('In-activate notification successful.')

			logger.info(logger_format('<-------  END  ------->', api_notification_active.__name__))
			return Response({
				'status': status.HTTP_200_OK,
				'result': True,
				'message': message
			}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_active.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_delete'),))
def api_notification_delete(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_delete.__name__))
	errors = {}
	serial = request.POST.get('serial', '').strip()
	schedule_id = request.POST.get('schedule_id', '').strip()
	is_delete = request.POST.get('is_delete', '0').strip()

	logger.info(logger_format('Check serial', api_notification_delete.__name__))
	if not serial:
		errors.update({'serial': _('This field is required.')})

	if not errors:
		if int(is_delete) == 1:
			Schedule.objects.filter(serial=serial).delete()
		else:
			try:
				obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule_id)
				obj_schedule.delete()
			except Schedule.DoesNotExist:
				logger.error(logger_format('Schedule does not exists.', api_notification_delete.__name__))
				errors.update({'message': _('Schedule does not exists.')})

		logger.info(logger_format('<-------  END  ------->', api_notification_delete.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': _('You have successfully deleted the notification.')
		}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_delete.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
