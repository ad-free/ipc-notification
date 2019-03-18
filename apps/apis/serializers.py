# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from rest_framework import serializers, status, exceptions

from apps.notifications.models import GCM, APNS
from apps.users.models import Customer
from apps.schedule.models import Schedule

from apps.apis.utils import update_or_create_device, single_subscribe_or_publish, message_format

from ast import literal_eval

import uuid
import json
import time

LETTER_TYPE = (
	(201, 'Payment system'),
	(202, 'Camera Notification'),
	(203, 'Camera Change Owner'),
	(204, 'Gift code Sending'),
)

NOTIFICATION_TYPE = (
	(101, 'Camera motion'),
	(102, 'User Inbox'),
)


class APIException(exceptions.APIException):
	status_code = status.HTTP_200_OK
	default_code = status.HTTP_400_BAD_REQUEST

	def __init__(self, detail, status_code=None):
		self.detail = detail
		if status_code is not None:
			self.status_code = status_code


class RegisterSerializer(serializers.Serializer):
	id = serializers.UUIDField(read_only=True, default=uuid.uuid1)
	username = serializers.CharField(max_length=32, required=True)
	password = serializers.CharField(max_length=255, required=True)
	platform = serializers.CharField(max_length=255, required=True)
	device_token = serializers.CharField(max_length=255, required=True)
	bundle = serializers.CharField(max_length=100, required=True)

	def create(self, validated_data):
		""" Create register account """

		errors = {}
		result = {'success': '', 'message': ''}
		username = validated_data.get('username', '')
		password = validated_data.get('password', '')
		platform = validated_data.get('platform', '')
		device_token = validated_data.get('device_token', '')
		bundle = validated_data.get('bundle', '')
		name = platform + '_' + bundle

		if platform == 'apns':
			result = update_or_create_device(APNS, name, device_token, username, password, False)
		elif platform == 'fcm':
			result = update_or_create_device(GCM, name, device_token, username, password, False)

		if result['success']:
			raise APIException({
				'status': status.HTTP_200_OK,
				'result': True,
				'message': result['message']
			})
		elif result['success'] is False:
			errors.update({'message': result['message']})
		else:
			errors.update({'message': 'Your platform is inaccurate.'})

		raise APIException({
			'status': status.HTTP_400_BAD_REQUEST,
			'result': False,
			'errors': errors if errors else 'Check your platform and bundle fields.'
		})


class UpdateSerializer(serializers.Serializer):
	id = serializers.UUIDField(read_only=True, default=uuid.uuid1)
	username = serializers.CharField(max_length=32, required=True)
	new_username = serializers.CharField(max_length=32, required=False, allow_blank=True, allow_null=True)
	serial = serializers.CharField(max_length=32, required=False)
	schedule = serializers.CharField(max_length=255, required=False)
	is_unshared = serializers.CharField(max_length=50, required=False)

	def create(self, validated_data):
		""" Update schedule """

		errors = {}
		username = validated_data.get('username', '')
		new_username = validated_data.get('new_username', '')
		serial = validated_data.get('serial', '')
		schedule_list = validated_data.get('schedule', '')
		is_unshared = validated_data.get('is_unshared', '')

		if not new_username:
			if not serial:
				errors.update({'serial': 'This field is required.'})
			if not schedule_list:
				errors.update({'schedule': 'This field is required.'})
			if not is_unshared:
				errors.update({'is_unshared': 'This field is required.'})

		if not errors:
			try:
				user = Customer.objects.get(username=username)
			except Customer.DoesNotExist:
				errors.update({'message': 'User does not exists.'})
			else:
				if len(new_username) > 0:
					try:
						Customer.objects.get(username=new_username)
						errors.update({'message': 'New username always exists.'})
						raise APIException({
							'status': status.HTTP_400_BAD_REQUEST,
							'result': False,
							'errors': errors
						})
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
				raise APIException({
					'status': status.HTTP_200_OK,
					'result': True,
					'message': 'You have successfully updated.'
				})

		raise APIException({
			'status': status.HTTP_400_BAD_REQUEST,
			'result': False,
			'errors': errors
		})


class DeleteSerializer(serializers.Serializer):
	id = serializers.UUIDField(read_only=True, default=uuid.uuid1)
	serial = serializers.CharField(max_length=32, required=True)
	schedule_id = serializers.CharField(max_length=255, required=True)
	is_delete = serializers.IntegerField(default=0)

	def create(self, validated_data):
		""" Delete schedule """

		errors = {}
		message = {}
		serial = validated_data.get('serial', '')
		schedule_list = validated_data.get('schedule_id', '')
		is_delete = validated_data.get('is_delete', '')

		if is_delete == 1:
			Schedule.objects.filter(serial=serial)
		else:
			for schedule in literal_eval(schedule_list):
				try:
					obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
					obj_schedule.delete()
					message.update({schedule: 'The schedule has been successfully deleted.'})
				except Schedule.DoesNotExist:
					errors.update({schedule: 'Schedule does not exists.'})
				except Exception as e:
					errors.update({'message': str(e)})

		raise APIException({
			'status': status.HTTP_200_OK if not errors else status.HTTP_400_BAD_REQUEST,
			'result': True if not errors else False,
			'message': message,
			'errors': errors
		})


class ActiveSerializer(serializers.Serializer):
	id = serializers.UUIDField(read_only=True, default=uuid.uuid1)
	username = serializers.CharField(max_length=32, required=True)
	serial = serializers.CharField(max_length=32, required=True)
	schedule_id = serializers.CharField(max_length=255, required=True)
	is_active = serializers.IntegerField(default=0)

	def create(self, validated_data):
		""" Active schedule """

		errors = {}
		username = validated_data.get('username', '')
		serial = validated_data.get('serial', '')
		schedule_id = validated_data.get('schedule_id', '')
		is_active = validated_data.get('is_active', '')

		try:
			user = Customer.objects.get(username=username)
		except Customer.DoesNotExist:
			errors.update({'message': 'User does not exists.'})
		else:
			message = {}
			if is_active == 1:
				for schedule in literal_eval(schedule_id):
					try:
						obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
						obj_schedule.user.add(user)
						message.update({schedule: 'Activate notification successful.'})
					except Schedule.DoesNotExist:
						errors.update({schedule: 'Schedule does not exists.'})
			else:
				for schedule in literal_eval(schedule_id):
					try:
						obj_schedule = Schedule.objects.get(serial=serial, schedule_id=schedule)
						obj_schedule.user.remove(user)
						message.update({schedule: 'In-activate notification successful.'})
					except Schedule.DoesNotExist:
						errors.update({schedule: 'Schedule does not exists.'})

			raise APIException({
				'status': status.HTTP_200_OK,
				'result': True,
				'message': message,
				'errors': errors
			})

		raise APIException({
			'status': status.HTTP_400_BAD_REQUEST,
			'result': False,
			'errors': errors
		})


class SendSerializer(serializers.Serializer):
	id = serializers.UUIDField(read_only=True, default=uuid.uuid1)
	phone_number = serializers.CharField(max_length=30, required=True)
	title = serializers.CharField(max_length=100, required=True)
	message = serializers.CharField(max_length=1024, required=True)
	letter_type = serializers.IntegerField(required=True)
	attachment = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
	notification_title = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
	notification_body = serializers.CharField(max_length=1024, required=False, allow_blank=True, allow_null=True)
	notification_type = serializers.IntegerField(required=True)

	def create(self, validated_data):
		errors = {}
		phone_number = validated_data.get('phone_number', '')
		title = validated_data.get('title', '')
		message = validated_data.get('message', '')
		letter_type = validated_data.get('letter_type', '')
		attachment = validated_data.get('attachment', '')
		notification_title = validated_data.get('notification_title', '')
		notification_body = validated_data.get('notification_body', '')
		notification_type = validated_data.get('notification_type', '')

		try:
			user = Customer.objects.get(username=phone_number)
		except Customer.DoesNotExist:
			errors.update({'message': 'User does not exists.'})
		else:
			topic = settings.USER_TOPIC_STATUS.format(name=phone_number)
			msg = single_subscribe_or_publish(topic=topic, is_subscribe=True)
			data = json.loads(msg.payload)
			if 'status' in data:
				apns_list = APNS.objects.distinct().filter(user=user)
				gcm_list = GCM.objects.distinct().filter(user=user)
				message = message_format(
						title=u'{}'.format(title),
						body=u'{}'.format(message),
						url=u'{}'.format('www.prod-alert.iotc.vn'),
						acm_id=uuid.uuid1().hex,
						time=int(time.time()),
						camera_serial='',
						letter_type=letter_type,
						attachment=attachment,
						notification_title=notification_title,
						notification_body=notification_body,
						notification_type=notification_type
				)
				single_subscribe_or_publish(
						topic=settings.USER_TOPIC_ANNOUNCE.format(name=phone_number),
						payload=json.dumps(message),
						is_publish=True
				)
				if data['status'] == 'online':
					if apns_list.exists():
						device_message = json.dumps({
							'aps': {
								'alert': message,
								'sound': 'default',
								'content-available': 1
							}
						})
						single_subscribe_or_publish(
								topic=settings.USER_TOPIC_ANNOUNCE.format(name=phone_number),
								payload=device_message,
								is_publish=True
						)
					if gcm_list.exists():
						device_message = json.dumps({
							'data': message,
							'sound': 'default',
							'content-available': 1
						})
						single_subscribe_or_publish(
								topic=settings.USER_TOPIC_ANNOUNCE.format(name=phone_number),
								payload=device_message,
								is_publish=True
						)
				else:
					if apns_list.exists():
						for obj_apns in apns_list:
							try:
								obj_apns.send_message(message=message, sound='default', content_available=1)
							except Exception as e:
								if 'Unregistered' in str(e):
									obj_apns.delete()
								pass
					if gcm_list.exists():
						for obj_gcm in gcm_list:
							try:
								obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)
							except Exception as e:
								if 'Unregistered' in str(e):
									obj_gcm.delete()
								pass
				raise APIException({
					'status': status.HTTP_200_OK,
					'result': True,
					'message': 'Send notifications to users successfully.'
				})
			else:
				errors.update({'message': 'The user\'s status cannot be determined.'})
		raise APIException({
			'status': status.HTTP_400_BAD_REQUEST,
			'result': False,
			'errors': errors
		})
