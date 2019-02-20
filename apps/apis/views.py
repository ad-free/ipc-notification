# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
from ast import literal_eval

import logging

logger = logging.getLogger('')


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_register'),))
def api_notification_register(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_register.__name__))
	errors = {}
	result = {'success': '', 'message': ''}
	username = request.POST.get('username', '').strip()
	password = request.POST.get('password', '')
	platform = request.POST.get('platform', '').strip()
	device_token = request.POST.get('device_token', '').strip()
	bundle = request.POST.get('bundle', '').strip()
	name = platform + '_' + bundle

	logger.info(logger_format('Check your platform', api_notification_register.__name__))
	if platform == 'apns':
		result = update_or_create_device(APNS, name, device_token, username, password, False)
	elif platform == 'fcm':
		result = update_or_create_device(GCM, name, device_token, username, password, True)

	if result['success']:
		logger.info(logger_format('<-------  END  ------->', api_notification_register.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': result['message']
		}, status=status.HTTP_200_OK)
	elif result['success'] is False:
		errors.update({'message': result['message']})
		logger.error(logger_format(result['message'], api_notification_register.__name__))
	else:
		errors.update({'message': _('Your platform is inaccurate.')})
		logger.error(logger_format('Your platform is inaccurate.', api_notification_register.__name__))

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
	new_username = request.POST.get('new_username', '').strip()
	serial = request.POST.get('serial', '').strip()
	schedule_list = request.POST.get('schedule', '').strip()
	is_unshared = request.POST.get('is_unshared', '').strip()

	if not username:
		errors.update({'username': _('This field is required.')})
	if not new_username:
		if not serial:
			errors.update({'serial': _('This field is required.')})
		if not schedule_list:
			errors.update({'schedule_list': _('This field is required.')})
		if not is_unshared:
			errors.update({'is_unshared': _('This field is required.')})

	if not errors:
		try:
			user = Customer.objects.get(username=username)
		except Customer.DoesNotExist:
			logger.error(logger_format('User does not exists.', api_notification_update.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			if len(new_username) > 0:
				try:
					Customer.objects.get(username=new_username)
					errors.update({'message': _('New username always exists.')})
					logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
					return Response({
						'status': status.HTTP_400_BAD_REQUEST,
						'result': False,
						'errors': errors
					}, status=status.HTTP_200_OK)
				except Customer.DoesNotExist:
					user.username = new_username
					user.save()
			else:
				if is_unshared == '1':
					obj_schedule = Schedule.objects.filter(serial=serial)
					if obj_schedule.exists():
						for schedule in obj_schedule:
							schedule.user.remove(user)
				else:
					for schedule in literal_eval(schedule_list):
						data_default = {
							'start_time': schedule['begin_at'],
							'end_time': schedule['end_at'],
							'repeat_status': int(schedule['repeat_status']),
							'is_active': True if int(schedule['is_active']) == 1 else False
						}
						if int(schedule['repeat_status']) == 0:
							data_default.update({'date': schedule['repeat_at'], 'repeat_at': None})
						else:
							data_default.update({'date': None, 'repeat_at': schedule['repeat_at']})
						obj_schedule, schedule_created = Schedule.objects.update_or_create(
								serial=serial,
								schedule_id=schedule['schedule_id'],
								defaults=data_default
						)
						if int(schedule['is_active']) == 1:
							obj_schedule.user.add(user)
						else:
							obj_schedule.user.remove(user)
							if obj_schedule.user.count() == 0:
								obj_schedule.delete()
			logger.info(logger_format('<-------  END  ------->', api_notification_update.__name__))
			return Response({
				'status': status.HTTP_200_OK,
				'result': True,
				'message': _('You have successfully updated.')
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
			try:
				if int(is_active) == 1:
					for schedule in literal_eval(schedule_id):
						try:
							obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
							obj_schedule.user.add(user)
						except Schedule.DoesNotExist:
							logger.warning(logger_format('Schedule does not exists.', api_notification_active.__name__))
					message = _('Activate notification successful.')
				else:
					for schedule in literal_eval(schedule_id):
						try:
							obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
							obj_schedule.user.remove(user)
						except Schedule.DoesNotExist:
							logger.warning(logger_format('Schedule does not exists.', api_notification_active.__name__))
					message = _('In-activate notification successful.')
			except Exception as e:
				logger.warning(logger_format(e, api_notification_active.__name__))
				message = _('Please check your parameters.')

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
	schedule_list = request.POST.get('schedule_id', '').strip()
	is_delete = request.POST.get('is_delete', '').strip()

	logger.info(logger_format('Check serial', api_notification_delete.__name__))
	if not serial:
		errors.update({'serial': _('This field is required.')})

	if not errors:
		if is_delete == '1':
			Schedule.objects.filter(serial=serial).delete()
		else:
			try:
				for schedule in literal_eval(schedule_list):
					obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
					obj_schedule.delete()
			except Schedule.DoesNotExist:
				logger.warning(logger_format('Schedule does not exists.', api_notification_delete.__name__))
				errors.update({'message': _('Schedule does not exists.')})
			except Exception as e:
				logger.warning(logger_format(e, api_notification_delete.__name__))
				errors.update({'message': _('Please check your parameters.')})

		logger.info(logger_format('<-------  END  ------->', api_notification_delete.__name__))
		return Response({
			'status': status.HTTP_200_OK,
			'result': True,
			'message': _('You have successfully deleted the notification.') if not errors else errors['message']
		}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_delete.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
