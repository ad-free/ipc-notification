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
from datetime import datetime, timedelta
from ast import literal_eval

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
			client.subscribe(settings.USER_TOPIC_STATUS.format(name='+'))
			client.subscribe(settings.CAMERA_TOPIC_DATA.format(name='+'))
		else:
			self.stdout.write('Connection failed.')

	def on_message(self, client, userdata, message):
		data = json.loads(message.payload)
		serial = message.topic.split('/')[1]
		push_notification = False
		try:
			obj_schedule = Schedule.objects.get(serial=serial)
		except Schedule.DoesNotExist:
			pass
		else:
			for schedule in literal_eval(obj_schedule.schedule):
				begin_at = schedule['begin_at'].split(':')
				end_at = schedule['end_at'].split(':')
				if schedule['repeat_status'] == 1:
					if datetime.now().weekday() in schedule['repeat_at']['days']:
						now = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
						if (timedelta(hours=int(begin_at[0]), minutes=int(begin_at[1])) < now) and (now < timedelta(hours=int(end_at[0]), minutes=int(end_at[1]))):
							push_notification = True
							break
				elif schedule['repeat_status'] == 0:
					start_time = datetime.strptime('{date} {hour}:{minutes}'.format(date=schedule['repeat_at']['days'], hour=int(begin_at[0]), minutes=int(begin_at[1])), settings.DATE_TIME_FORMAT)
					end_time = datetime.strptime('{date} {hour}:{minutes}'.format(date=schedule['repeat_at']['days'], hour=int(end_at[0]), minutes=int(end_at[1])), settings.DATE_TIME_FORMAT)
					if (start_time < datetime.now()) and (datetime.now() < end_time):
						push_notification = True
						break

			if push_notification:
				apns_list = APNSDevice.objects.filter(name=obj_schedule.user)
				gcm_list = GCMDevice.objects.filter(name=obj_schedule.user)
				if apns_list.exists():
					for obj_apns in apns_list:
						obj_apns.send_message(message=message, sound='default', content_available=1)
				elif gcm_list.exists():
					for obj_gcm in gcm_list:
						obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)

		# if data['status'] == 'online':
		# 	message = message_format(title='Testing', body='Testing', url='www.alert.iotc.vn', acm_id=uuid.uuid1().hex, time=time.time(), serial=serial)
		# 	test = json.dumps({
		# 		'aps': {
		# 			'alert': message,
		# 			'sound': 'default',
		# 			'content-available': 1
		# 		}
		# 	})
		# 	client.publish('user/84971667819/data/announce', test)
		# 	client.publish('customer/inbox/data/announce', test)
		# 	self.stdout.write('Publish completed.')
		# else:
		# 	message = message_format(title='Testing', body='Testing', url='www.alert.iotc.vn', acm_id=uuid.uuid1(), time=time.time(), serial=serial)
		# 	try:
		# 		obj_schedule = Schedule.objects.get(serial=serial)
		# 	except Schedule.DoesNotExist:
		# 		pass
		# 	else:
		# 		apns_list = APNSDevice.objects.filter(name=obj_schedule.user)
		# 		gcm_list = GCMDevice.objects.filter(name=obj_schedule.user)
		# 		if apns_list.exists():
		# 			for obj_apns in apns_list:
		# 				obj_apns.send_message(message=message, sound='default', content_available=1)
		# 		elif gcm_list.exists():
		# 			for obj_gcm in gcm_list:
		# 				obj_gcm.send_message(None, extra=message, use_fcm_notifications=False)
		# 	client.publish('customer/inbox/data/announce', message)
		# 	self.stdout.write('Publish completed.')
