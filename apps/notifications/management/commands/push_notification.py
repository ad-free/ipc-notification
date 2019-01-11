from __future__ import absolute_import

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from apps.commons.utils import logger_format
from apps.schedule.models import Schedule
from apps.users.models import Customer
from apps.notifications.models import GCM, APNS

from apps.apis.utils import message_format
from pytz import unicode
from datetime import datetime, timedelta
from threading import Thread

import paho.mqtt.client as mqtt
import uuid
import json
import time
import logging

logger = logging.getLogger('')


class Command(BaseCommand):
	help = unicode(_('Push notification to user.'))

	def add_arguments(self, parser):
		parser.add_argument('--serial', action='store', type=str, default=None, help=_('Camera serial'))

	def handle(self, *args, **options):
		client = mqtt.Client('iot-{}'.format(uuid.uuid1().hex))
		client.on_connect = self.on_connect
		client.on_message = self.on_message
		client.connect(host=settings.API_QUEUE_HOST, port=settings.API_QUEUE_PORT)
		client.username_pw_set(username=settings.API_ALERT_USERNAME, password=settings.API_ALERT_PASSWORD)
		client.loop_forever()

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.stdout.write('Connected to broker server.')
			for topic in settings.SUBSCRIBE_TOPICS:
				client.subscribe(topic.format(name='+'))
		else:
			self.stdout.write('Connection failed.')

	def on_message(self, client, userdata, message):
		data = json.loads(message.payload)
		serial = message.topic.split('/')[1]

		if message.topic.startswith('user'):
			try:
				obj_user = Customer.objects.get(username=serial)
			except Customer.DoesNotExist:
				pass
			else:
				if 'status' in data:
					if data['status'] == 'online':
						obj_user.is_online = True
					else:
						obj_user.is_online = False
					obj_user.save()
		else:
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

	def multiple_threading(self, push_notification, create_topic, client, user, serial):
		self.stdout.write('Start multiple threading.')
		message = message_format(
				title=u'{}'.format('Merry Christmas'),
				body=u'Kiss me with {number} times'.format(number=uuid.uuid1().hex),
				url=u'{}'.format('www.alert.iotc.vn'),
				acm_id=uuid.uuid1().hex,
				time=time.time(),
				serial=serial
		)
		t1 = Thread(target=push_notification, args=(client, user, message))
		t2 = Thread(target=create_topic, args=(client, user, message))
		t1.setDaemon(True)
		t2.setDaemon(True)
		t1.start()
		t2.start()

	def create_topic(self, client, user, message):
		client.publish(settings.CUSTOMER_TOPIC_ANNOUNCE.format(name='inbox'), json.dumps(message))
		self.stdout.write('Send message to customer system')

	def push_notification(self, client, user, message):
		apns_list = APNS.objects.distinct().filter(user=user)
		gcm_list = GCM.objects.distinct().filter(user=user)
		if user.is_online:
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
					try:
						obj_apns.send_message(message=message, sound='default', content_available=1)
					except Exception as e:
						logger.error(logger_format('{}-{}'.format(obj_apns.registration_id, e), self.push_notification.__name__))
						if 'Unregistered' in e:
							obj_apns.delete()
						pass
			if gcm_list.exists():
				for obj_gcm in gcm_list:
					try:
						obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)
					except Exception as e:
						logger.error(logger_format('{}-{}'.format(obj_gcm.registration_id, e), self.push_notification.__name__))
						if 'Unregistered' in e:
							obj_gcm.delete()
						pass
			self.stdout.write('Sent a notification to user.')
