from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _

from apps.schedule.models import Schedule

from pytz import unicode

import paho.mqtt.client as mqtt
import uuid
import json


class Command(BaseCommand):
	help = unicode(_('Push notification to user.'))

	def add_arguments(self, parser):
		parser.add_argument('serial', action='store', type=str, default=None, help=_('Subcribe topic'))

	def handle(self, *args, **options):
		if not options['serial']:
			raise CommandError(_('Serial required and must be only one'))
		obj_schedule = Schedule.objects.filter(serial=options['serial'])
		if obj_schedule.exists():
			client = mqtt.Client("iot-{}".format(uuid.uuid4()))
			client.on_connect = self.on_connect
			client.on_message = self.on_message
			client.connect(host='queue.iotc.vn', port=1883)
			client.username_pw_set(username='notify', password='ipcAlert!@#')
			client.loop_forever()
		else:
			raise CommandError('Schedule does not exists.')

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print("Connected to broker")
			client.subscribe("device/C100/data")
		else:
			print("Connection failed")

	def on_message(self, client, userdata, message):
		data = json.loads(message.payload)
		if data['status'] == 'Online':
			client.publish('device/0976237026/announce', 'Online')
			print('Online')
		else:
			client.publish('device/0976237026/announce', 'Offline')
			print('Offline')

