# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from apps.apis.serializers import LETTER_TYPE, NOTIFICATION_TYPE
from apps.commons.utils import Formatter
from apps.schedule.models import Schedule
from apps.notifications.models import GCM, APNS

from apps.apis.utils import message_format
from datetime import datetime, timedelta
from threading import Thread

import paho.mqtt.client as mqtt
import uuid
import json
import time
import logging
import ssl
import random

logger = logging.getLogger('')
formatter = Formatter()


class Command(BaseCommand):
	help = _('Push notification to user.')
	
	def add_arguments(self, parser):
		parser.add_argument('--serial', action='store', type=str, default=None, help=_('Camera serial'))

	def handle(self, *args, **options):
		self.status = {}
		client = mqtt.Client('iot-{}'.format(uuid.uuid1().hex))
		client.on_connect = self.on_connect
		client.on_message = self.on_message
		client.tls_set(
				ca_certs=settings.CA_ROOT_CERT_FILE,
				certfile=settings.CA_ROOT_CERT_CLIENT,
				keyfile=settings.CA_ROOT_CERT_KEY,
				cert_reqs=ssl.CERT_NONE,
				tls_version=settings.CA_ROOT_TLS_VERSION,
				ciphers=settings.CA_ROOT_CERT_CIPHERS
		)
		# client.tls_insecure_set(False)
		client.connect(host=settings.API_QUEUE_HOST, port=settings.API_QUEUE_PORT)
		client.username_pw_set(username=settings.API_ALERT_USERNAME, password=settings.API_ALERT_PASSWORD)
		client.loop_forever()

	def on_connect(self, client, userdata, flags, rc):
		self.stdout.write('Connecting.......')
		if rc == 0:
			self.stdout.write('Connected to broker server.')
			for topic in settings.SUBSCRIBE_TOPICS:
				client.subscribe(topic.format(name='+'))
		else:
			self.stdout.write('Connection failed.')

	def on_message(self, client, userdata, message):
		try:
			data = json.loads(message.payload)
			serial = message.topic.split('/')[1]
			if message.topic.startswith('user'):
				username = message.topic.split('/')[1]
				self.status.update({username: data['status']})
		except Exception as e:
			logger.error(formatter.logger(message=str(e), func_name=self.on_message.__name__))
			data = {}
			serial = ''
		
		if {'Status', 'Type'} <= data.keys():
			logger.error(formatter.logger(message=u'{}-{}-{}-{}'.format(data['StartTime'], data['Address'], data['SerialID'], data['Event']), func_name=data['Type']))
			if data['Status'] == 'Start' and data['Type'] == 'Alarm':
				obj_schedule = Schedule.objects.filter(serial=serial)
				if obj_schedule.exists():
					for schedule in obj_schedule:
						if schedule.repeat_status:
							if datetime.now().weekday() in json.loads(schedule.repeat_at):
								now = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
								if (timedelta(hours=schedule.start_time.hour, minutes=schedule.start_time.minute) <= now) and (
										now <= timedelta(hours=schedule.end_time.hour, minutes=schedule.end_time.minute)):
									for user in schedule.user.all():
										self.multiple_threading(self.push_notification, self.create_topic, client, user, serial)
									break
						else:
							start_time = datetime.strptime('{date} {hour}:{minutes}'.format(
								date=schedule.date,
								hour=schedule.start_time.hour,
								minutes=schedule.start_time.minute
							), settings.DATE_TIME_FORMAT)
							end_time = datetime.strptime('{date} {hour}:{minutes}'.format(
								date=schedule.date,
								hour=schedule.end_time.hour,
								minutes=schedule.end_time.minute
							), settings.DATE_TIME_FORMAT)
							if (start_time <= datetime.now()) and (datetime.now() <= end_time):
								for user in schedule.user.all():
									self.multiple_threading(self.push_notification, self.create_topic, client, user, serial)
								break

	def multiple_threading(self, push_notification, create_topic, client, user, serial, data):
		self.stdout.write('Start multiple threading.')
		title_default = [
			_('Some strangers has been detected...'),
			_('A moment has been captured by you'),
			_('Some movement has been recorded...'),
		]
		message = message_format(
				title=u'{}'.format(random.choice(title_default)),
				body=data['Descrip'] if data['Descrip'] else u'{}'.format('Phát hiện chuyển động.'),
				url=u'{}'.format('www.prod-alert.iotc.vn'),
				acm_id=uuid.uuid1().hex,
				time=int(time.time()),
				camera_serial=serial,
				letter_type=LETTER_TYPE[1][0],
				attachment='',
				notification_title='',
				notification_body='',
				notification_type=NOTIFICATION_TYPE[0][0]
		)
		t1 = Thread(target=push_notification, args=(client, user, message))
		t2 = Thread(target=create_topic, args=(client, user, message))
		t1.setDaemon(True)
		t2.setDaemon(True)
		t1.start()
		t2.start()

	def create_topic(self, client, user, message):
		client.publish(settings.USER_TOPIC_ANNOUNCE.format(name=user.username), json.dumps(message))
		self.stdout.write('Send message to customer system')

	def push_notification(self, client, user, message):
		apns_list = APNS.objects.distinct().filter(user=user)
		gcm_list = GCM.objects.distinct().filter(user=user)

		try:
			if self.status[user.username] == 'online':
				if apns_list.exists():
					device_message = json.dumps({
						'aps': {
							'alert': message,
							'sound': 'default',
							'content-available': 1
						}
					})
					client.publish(settings.USER_TOPIC_ANNOUNCE.format(name=user.username), device_message)
				if gcm_list.exists():
					device_message = json.dumps({
						'data': message,
						'sound': 'default',
						'content-available': 1
					})
					client.publish(settings.USER_TOPIC_ANNOUNCE.format(name=user.username), device_message)
				self.stdout.write('Publish message completed.')
			else:
				if apns_list.exists():
					for obj_apns in apns_list:
						if obj_apns.active:
							try:
								obj_apns.send_message(message=message, sound='default', content_available=1)
							except Exception as e:
								logger.error(formatter.logger(message=u'{}-{}'.format(obj_apns.registration_id, e), func_name=self.push_notification.__name__))
								if 'Unregistered' in str(e):
									obj_apns.delete()
								pass
				if gcm_list.exists():
					for obj_gcm in gcm_list:
						if obj_gcm.active:
							try:
								obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)
							except Exception as e:
								logger.error(formatter.logger(message=u'{}-{}'.format(obj_gcm.registration_id, e), func_name=self.push_notification.__name__))
								if 'Unregistered' in str(e):
									obj_gcm.delete()
								pass
				self.stdout.write('Sent a notification to user.')
		except KeyError as e:
			logger.error(formatter.logger(message=u'{}-{}'.format(user.username, e), func_name=self.push_notification.__name__))
		connection.close()
