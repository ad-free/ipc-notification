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
from ..commons.utils import Formatter

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
formatter = Formatter()


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
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_register.__name__))
	errors = {}
	result = {'success': '', 'message': ''}
	username = request.data.get('username', '').strip()
	password = request.data.get('password', '')
	platform = request.data.get('platform', '').strip()
	device_token = request.data.get('device_token', '').strip()
	bundle = request.data.get('bundle', '').strip()
	name = platform + '_' + bundle
	
	logger.info(formatter.logger(message='Check your platform', func_name=api_notification_register.__name__))
	if platform == 'apns':
		result = update_or_create_device(APNS, name, device_token, username, password, False)
	elif platform == 'fcm':
		result = update_or_create_device(GCM, name, device_token, username, password, True)
	
	if result['success']:
		logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_register.__name__))
		return Response(formatter.response(
				status=formatter.status['OK'],
				result=True,
				message=result['message']
		), status=status.HTTP_200_OK)
	elif result['success'] is False:
		errors.update({'message': result['message']})
		logger.error(formatter.logger(message=result['message'], func_name=api_notification_register.__name__))
	else:
		errors.update({'message': _('Your platform is inaccurate.')})
		logger.error(formatter.logger(message='Your platform is inaccurate.', func_name=api_notification_register.__name__))
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_register.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=False,
			errors=errors
	), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=UpdateSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_update'),))
def api_notification_update(request):
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_update.__name__))
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
			logger.error(formatter.logger(message='User does not exists.', func_name=api_notification_update.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			if len(new_username) > 0:
				try:
					Customer.objects.get(username=new_username)
					errors.update({'message': _('New username always exists.')})
					logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_update.__name__))
					return Response(formatter.response(
							status=formatter.status['BAD_REQUEST'],
							result=False,
							errors=errors
					), status=status.HTTP_200_OK)
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
			logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_update.__name__))
			return Response(formatter.response(
					status=formatter.status['OK'],
					result=True,
					message=_('You have successfully updated.')
			), status=status.HTTP_200_OK)
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_update.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=False,
			errors=errors
	), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=ActiveSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_active'),))
def api_notification_active(request):
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_active.__name__))
	errors = {}
	username = request.data.get('username', '').strip()
	serial = request.data.get('serial', '').strip()
	schedule_id = request.data.get('schedule_id', '').strip()
	is_active = request.data.get('is_active', '0').strip()
	
	logger.info(formatter.logger(message='Checking serial', func_name=api_notification_active.__name__))
	if not serial:
		errors.update({'serial': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking username', func_name=api_notification_active.__name__))
	if not username:
		errors.update({'username': _('This field is required.')})
	
	logger.info(formatter.logger(message='Validate parameters', func_name=api_notification_active.__name__))
	if not errors:
		try:
			user = Customer.objects.get(username=username)
		except Customer.DoesNotExist:
			logger.error(formatter.logger(message='User does not exists.', func_name=api_notification_active.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			try:
				if int(is_active) == 1:
					for schedule in literal_eval(schedule_id):
						try:
							obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
							obj_schedule.user.add(user)
						except Schedule.DoesNotExist:
							logger.warning(formatter.logger(message='Schedule does not exists.', func_name=api_notification_active.__name__))
					message = _('Activate notification successful.')
				else:
					for schedule in literal_eval(schedule_id):
						try:
							obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
							obj_schedule.user.remove(user)
						except Schedule.DoesNotExist:
							logger.warning(formatter.logger(message='Schedule does not exists.', func_name=api_notification_active.__name__))
					message = _('In-activate notification successful.')
			except Exception as e:
				logger.warning(formatter.logger(message=str(e), func_name=api_notification_active.__name__))
				message = _('Please check your parameters.')
			
			logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_active.__name__))
			return Response(formatter.response(
					status=formatter.status['OK'],
					result=True,
					message=message
			), status=status.HTTP_200_OK)
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_active.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=False,
			errors=errors
	), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=InActiveSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_inactive'),))
def api_notification_inactive(request):
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_inactive.__name__))
	errors = {}
	device_token = request.data.get('device_token', '').strip()
	username = request.data.get('username', '').strip()
	platform = request.data.get('platform', '').strip()
	
	logger.info(formatter.logger(message='Checking device token', func_name=api_notification_inactive.__name__))
	if not device_token:
		errors.update({'device_token': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking username', func_name=api_notification_inactive.__name__))
	if not username:
		errors.update({'username': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking platform', func_name=api_notification_inactive.__name__))
	if not platform:
		errors.update({'platform': _('This field is required.')})
	
	logger.info(formatter.logger(message='Validate parameters', func_name=api_notification_inactive.__name__))
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
				logger.error(formatter.logger(message='Platform is incorrect formatting.', func_name=api_notification_inactive.__name__))
			
			if not errors:
				logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_inactive.__name__))
				return Response(formatter.response(
						status=formatter.status['OK'],
						result=True,
						message=_('Disable sending notifications successfully.')
				), status=status.HTTP_200_OK)
		except Customer.DoesNotExist:
			logger.error(formatter.logger(message='The user does not exists.', func_name=api_notification_inactive.__name__))
			errors.update({'message': _('The user does not exists.')})
		except APNS.DoesNotExist:
			logger.error(formatter.logger(message='APNS does not exists.', func_name=api_notification_inactive.__name__))
			errors.update({'message': _('The device does not exists.')})
		except GCM.DoesNotExist:
			logger.error(formatter.logger(message='GCM does not exists.', func_name=api_notification_inactive.__name__))
			errors.update({'message': _('The device does not exists.')})
		except Exception as e:
			logger.error(formatter.logger(message=str(e), func_name=api_notification_inactive.__name__))
			errors.update({'message': _('Server is error. Please try again later.')})
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_inactive.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=False,
			errors=errors
	), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=DeleteSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_delete'),))
def api_notification_delete(request):
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_delete.__name__))
	errors = {}
	serial = request.data.get('serial', '').strip()
	schedule_list = request.data.get('schedule_id', '').strip()
	is_delete = request.data.get('is_delete', '').strip()
	
	logger.info(formatter.logger(message='Checking serial', func_name=api_notification_delete.__name__))
	if not serial:
		errors.update({'serial': _('This field is required.')})
	
	logger.info(formatter.logger(message='Validate parameters', func_name=api_notification_delete.__name__))
	if not errors:
		if is_delete == '1':
			Schedule.objects.filter(serial=serial).delete()
		else:
			try:
				for schedule in literal_eval(schedule_list):
					obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
					obj_schedule.delete()
			except Schedule.DoesNotExist:
				logger.warning(formatter.logger(message='Schedule does not exists.', func_name=api_notification_delete.__name__))
				errors.update({'message': _('Schedule does not exists.')})
			except Exception as e:
				logger.warning(formatter.logger(message=str(e), func_name=api_notification_delete.__name__))
				errors.update({'message': _('Please check your parameters.')})
		
		logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_delete.__name__))
		return Response(formatter.response(
				status=formatter.status['OK'],
				result=True,
				message=_('You have successfully deleted the notification.')
		), status=status.HTTP_200_OK)
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_delete.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=False,
			errors=errors
	), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=SendSerializer)
@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_notification_send'),))
def api_notification_send(request):
	logger.info(formatter.logger(message='<-------  START  ------->', func_name=api_notification_send.__name__))
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
	
	logger.info(formatter.logger(message='Checking phone_number field', func_name=api_notification_send.__name__))
	if not phone_number:
		errors.update({'phone_number': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking title field', func_name=api_notification_send.__name__))
	if not title:
		errors.update({'title': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking body field', func_name=api_notification_send.__name__))
	if not body:
		errors.update({'body': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking letter_type field', func_name=api_notification_send.__name__))
	if not letter_type:
		errors.update({'letter_type': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking notification_type field', func_name=api_notification_send.__name__))
	if not notification_type:
		errors.update({'notification_type': _('This field is required.')})
	
	logger.info(formatter.logger(message='Checking acm_id field', func_name=api_notification_send.__name__))
	if not acm_id:
		errors.update({'acm_id': _('This field is required.')})
	
	logger.info(formatter.logger(message='Validate parameters', func_name=api_notification_send.__name__))
	if not errors:
		try:
			user = Customer.objects.get(username=phone_number)
		except Customer.DoesNotExist:
			logger.warning(formatter.logger(message='User does not exists.', func_name=api_notification_send.__name__))
			errors.update({'message': _('User does not exists.')})
		else:
			user_status = {'status': 'offline'}
			mqtt_client = mqtt.Client('{}-{}'.format(getattr(settings, 'MQTT_PREFIXES'), uuid.uuid1().hex))
			
			def on_connect(client, userdata, flags, rc):
				logger.info(formatter.logger(message='Connecting.....', func_name=api_notification_send.__name__))
				if rc == 0:
					logger.info(formatter.logger(message='Connected to broker server.', func_name=api_notification_send.__name__))
					for topics in settings.SUBSCRIBE_TOPICS:
						client.subscribe(topics.format(name=phone_number))
				else:
					logger.error(formatter.logger(message='Connection failed.', func_name=api_notification_send.__name__))
			
			def on_message(client, userdata, msg):
				data = json.loads(msg.payload)
				if 'status' in data:
					user_status['status'] = data['status']
				else:
					logger.warning(formatter.logger(message='The user\'s status cannot be determined.', func_name=api_notification_send.__name__))
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
				logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_send.__name__))
				return Response(formatter.response(
						status=formatter.status['OK'],
						result=True,
						message=_('Send notifications to users successfully.')
				), status=status.HTTP_200_OK)
	
	logger.info(formatter.logger(message='<-------  END  ------->', func_name=api_notification_send.__name__))
	return Response(formatter.response(
			status=formatter.status['BAD_REQUEST'],
			result=True,
			errors=errors
	), status=status.HTTP_200_OK)
