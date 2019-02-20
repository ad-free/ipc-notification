# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rest_framework import status

from .config import *

import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


class AnimalTestCase(TestCase):
	def setUp(self):
		self.url = ''
		self.gis = API_ALERT_GIS
		self.content_type = 'application/json'

	def test_register(self):
		self.url = API_ALERT_LIST['register'].format(protocol=API_ALERT_PROTOCOL, host=API_ALERT_HOST)
		cases = [
			{
				"username": "8497623702",
				"password": "f66edb256eeaca",
				"platform": "apns",
				"device_token": "fcc530639f6e362c5277b7209b708fa004e9",
				"bundle": "fcc530639f6e362c5277b7209b708fa004e9"
			},
			{
				"username": "8497623707",
				"password": "f66edb256eea99",
				"platform": "fcm",
				"device_token": "fcc530639f6e362c5277b7209b708fa004e9",
				"bundle": "fcc530639f6e362c5277b7209b708fa004e9"
			}
		]

		for case in cases:
			request = Request(url=self.url, data=urlencode(case).encode(), headers={'gis': self.gis})
			data = urlopen(request).read().decode('utf-8')
			data = json.loads(data)
			if data['result']:
				self.assertIs(data['status'], status.HTTP_200_OK, 'Completed.')
			else:
				self.assertNotEqual(data['status'], status.HTTP_400_BAD_REQUEST, data['errors']['message'])

	def test_update(self):
		pass

	def test_delete(self):
		pass

	def test_active(self):
		pass
