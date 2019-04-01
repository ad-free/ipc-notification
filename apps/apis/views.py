# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..users.models import Customer
from ..schedule.models import Schedule
from ..notifications.models import GCM, APNS

from ..apis.utils import APIAccessPermission, update_or_create_device, push_notification, connect_mqtt_server
from ..commons.utils import logger_format

from .serializers import (
	RegisterSerializer, UpdateSerializer,
	DeleteSerializer, ActiveSerializer,
	InActiveSerializer, SendSerializer
)

from functools import partial
from ast import literal_eval

import paho.mqtt.client as mqtt
import logging
import json
import uuid

logger = logging.getLogger('')


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_auth_sign_in'),))
def api_auth_sign_in(request):
	pass


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_auth_sign_out'),))
def api_auth_sign_out(request):
	pass


@swagger_auto_schema(methods=['post'], request_body=RegisterSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_register'),))
def api_notification_register(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_register.__name__))
	errors = {}
	result = {'success': '', 'message': ''}
	username = request.data.get('username', '').strip()
	password = request.data.get('password', '')
	platform = request.data.get('platform', '').strip()
	device_token = request.data.get('device_token', '').strip()
	bundle = request.data.get('bundle', '').strip()
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


@swagger_auto_schema(methods=['post'], request_body=UpdateSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_update'),))
def api_notification_update(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_update.__name__))
	errors = {}
	username = request.data.get('username', '').strip()
	new_username = request.data.get('new_username', '').strip()
	serial = request.data.get('serial', '').strip()
	schedule_list = request.data.get('schedule', '').strip()
	is_unshared = request.data.get('is_unshared', '').strip()

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


@swagger_auto_schema(methods=['post'], request_body=ActiveSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_active'),))
def api_notification_active(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_active.__name__))
	errors = {}
	username = request.data.get('username', '').strip()
	serial = request.data.get('serial', '').strip()
	schedule_id = request.data.get('schedule_id', '').strip()
	is_active = request.data.get('is_active', '0').strip()

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


@swagger_auto_schema(methods=['post'], request_body=InActiveSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_inactive'),))
def api_notification_inactive(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_inactive.__name__))
	errors = {}
	device_token = request.data.get('device_token', '').strip()
	username = request.data.get('username', '').strip()
	platform = request.data.get('platform', '').strip()

	if not device_token:
		errors.update({'device_token': _('This field is required.')})
	if not username:
		errors.update({'username': _('This field is required.')})
	if not platform:
		errors.update({'platform': _('This field is required.')})

	if not errors:
		try:
			user = Customer.objects.get(username=username)
			if platform == 'apns':
				apns = APNS.objects.get(registration_id=device_token, user=user)
				apns.active = False
				apns.save()
			elif platform == 'gcm':
				gcm = GCM.objects.get(registration_id=device_token, user=user)
				gcm.active = False
				gcm.save()
			else:
				errors.update({'platform': _('Incorrect formatting.')})

			if not errors:
				logger.info(logger_format('<-------  END  ------->', api_notification_inactive.__name__))
				return Response({
					'status': status.HTTP_200_OK,
					'result': True,
					'message': _('Disable sending notifications successfully.'),
				}, status=status.HTTP_200_OK)
		except Customer.DoesNotExist:
			logger.error(logger_format('The user does not exists.', api_notification_inactive.__name__))
			errors.update({'message': _('The user does not exists.')})
		except APNS.DoesNotExist:
			logger.error(logger_format('APNS does not exists.', api_notification_inactive.__name__))
			errors.update({'message': _('The device does not exists.')})
		except GCM.DoesNotExist:
			logger.error(logger_format('GCM does not exists.', api_notification_inactive.__name__))
			errors.update({'message': _('The device does not exists.')})
		except Exception as e:
			logger.error(logger_format(str(e), api_notification_inactive.__name__))
			errors.update({'message': _('Server is error. Please try again later.')})

	logger.info(logger_format('<-------  END  ------->', api_notification_inactive.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=DeleteSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_delete'),))
def api_notification_delete(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_delete.__name__))
	errors = {}
	serial = request.data.get('serial', '').strip()
	schedule_list = request.data.get('schedule_id', '').strip()
	is_delete = request.data.get('is_delete', '').strip()

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


@swagger_auto_schema(methods=['post'], request_body=SendSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_send'),))
def api_notification_send(request):
	logger.info(logger_format('<-------  START  ------->', api_notification_send.__name__))
	errors = {}
	acm_id = request.data.get('acm_id', '').strip()
	phone_number = request.data.get('phone_number', '').strip()
	title = request.data.get('title', '').strip()
	body = request.data.get('body', '').strip()
	letter_type = request.data.get('letter_type', '').strip()
	attachment = request.data.get('attachment', '').strip()
	notification_title = request.data.get('notification_title,', '').strip()
	notification_body = request.data.get('notification_body', '').strip()
	notification_type = request.data.get('notification_type', '').strip()

	if not phone_number:
		errors.update({'phone_number': _('This field is required.')})
	if not title:
		errors.update({'title': _('This field is required.')})
	if not body:
		errors.update({'body': _('This field is required.')})
	if not letter_type:
		errors.update({'letter_type': _('This field is required.')})
	if not notification_type:
		errors.update({'notification_type': _('This field is required.')})
	if not acm_id:
		errors.update({'acm_id': _('This field is required.')})

	if not errors:
		try:
			user = Customer.objects.get(username=phone_number)
		except Customer.DoesNotExist:
			logger.info(logger_format('User does not exists.', api_notification_send.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			user_status = {'status': 'offline'}
			mqtt_client = mqtt.Client('iot-{}'.format(uuid.uuid1().hex))

			def on_connect(client, userdata, flags, rc):
				logger.info(logger_format('Connecting.....', on_connect.__name__))
				if rc == 0:
					logger.info(logger_format('Connected to broker server.', on_connect.__name__))
					for topics in settings.SUBSCRIBE_TOPICS:
						client.subscribe(topics.format(name=phone_number))
				else:
					logger.info(logger_format('Connection failed.', on_connect.__name__))

			def on_message(client, userdata, msg):
				data = json.loads(msg.payload)
				if 'status' in data:
					user_status['status'] = data['status']
				else:
					errors.update({'message': _('The user\'s status cannot be determined.')})

			connect_mqtt_server(client=mqtt_client, on_connect=on_connect, on_message=on_message)

			result = push_notification(
					user=user,
					phone_number=phone_number,
					acm_id=acm_id,
					client=mqtt_client,
					data=user_status,
					title=title, body=body,
					letter_type=letter_type, attachment=attachment,
					notification_title=notification_title,
					notification_body=notification_body,
					notification_type=notification_type
			)
			if result:
				logger.info(logger_format('<-------  END  ------->', api_notification_send.__name__))
				return Response({
					'status': status.HTTP_200_OK,
					'result': True,
					'message': _('Send notifications to users successfully.')
				}, status=status.HTTP_200_OK)

	logger.info(logger_format('<-------  END  ------->', api_notification_send.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
