# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rest_framework import status
from django.conf import settings

from .config import *

import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import json
import os


class DeleteTestCase(TestCase):
	def setUp(self):
		self.url = ''
		self.gis = API_ALERT_GIS
		self.content_type = 'application/json'

		if not API_ALERT_LOCAL:
			self.url = API_ALERT_LIST['delete'].format(protocol=API_ALERT_PROTOCOL, host=API_ALERT_HOST)
		else:
			self.url = API_ALERT_LIST['delete'].format(protocol=API_ALERT_LOCAL_PROTOCOl, host=API_ALERT_LOCAL_HOST, port=API_ALERT_LOCAL_PORT)

	def test_delete(self):
		with open(os.path.join(settings.BASE_DIR, 'apps/apis/test/test_case_delete_api.json'), 'r') as f:
			cases = json.loads(f.read())

			for case in cases['data']:
				request = Request(url=self.url, data=urlencode(case).encode(), headers={'gis': self.gis})
				data = urlopen(request).read().decode('utf-8')
				data = json.loads(data)
				if data['result']:
					print('[+] %s' % case)
					print('[+] %s' % data['message'])
					print('[!] ----- Pass -----')
					self.assertIs(data['status'], status.HTTP_200_OK, 'Completed.')
				else:
					print('[X] %s' % case)
					self.assertNotEqual(data['status'], status.HTTP_400_BAD_REQUEST, data['errors']['message'])
