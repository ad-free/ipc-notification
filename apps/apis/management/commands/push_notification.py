from __future__ import absolute_import

from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _

from apps.schedule.models import Schedule
from push_notifications.models import GCMDevice, APNSDevice

from apps.apis.utils import message_format
from pytz import unicode
from datetime import datetime

import paho.mqtt.client as mqtt
import uuid
import json
import time


class Command(BaseCommand):
	help = unicode(_('Push notification to user.'))

	def add_arguments(self, parser):
		parser.add_argument('--serial', action='store', type=str, default=None, help=_('Camera serial'))

	def handle(self, *args, **options):
		client = mqtt.Client('iot-{}'.format(uuid.uuid4()))
		client.on_connect = self.on_connect
		client.on_message = self.on_message
		client.connect(host=settings.API_QUEUE_HOST, port=settings.API_QUEUE_PORT)
		client.username_pw_set(username=settings.API_ALERT_USERNAME, password=settings.API_ALERT_PASSWORD)
		client.loop_forever()

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.stdout.write('Connected to broker server.')
			client.subscribe('user/84971667819/status')
		else:
			self.stdout.write('Connection failed.')

	def on_message(self, client, userdata, message):
		data = json.loads(message.payload)
		name = message.topic.split('/')[1]
		if data['status'] == 'online':
			message = message_format(title='Testing', body='Testing', url='www.alert.iotc.vn', acm_id=uuid.uuid1(), time=time.time(), serial=name)
			test = json.dumps({
				'aps': {
					'alert': message,
					'sound': 'default',
					'content-available': 1
				}
			})
			client.publish('user/84971667819/data/announce', test)
			self.stdout.write('Publish completed.')
		else:
			message = message_format(title='Testing', body='Testing', url='www.alert.iotc.vn', acm_id=uuid.uuid1(), time=time.time(), serial=name)
			try:
				obj_schedule = Schedule.objects.get(serial=name)
			except Schedule.DoesNotExist:
				pass
			else:
				apns_list = APNSDevice.objects.filter(name=obj_schedule.user)
				gcm_list = GCMDevice.objects.filter(name=obj_schedule.user)
				if apns_list.exists():
					for obj_apns in apns_list:
						obj_apns.send_message(message=message, sound='default', content_available=1)
				elif gcm_list.exists():
					for obj_gcm in gcm_list:
						obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)
			self.stdout.write('Publish completed.')
