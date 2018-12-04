# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from push_notifications.models import (
	Device, GCMDeviceManager, APNSDeviceManager,
	WNSDeviceManager, WebPushDeviceManager,
	BROWSER_TYPES, CLOUD_MESSAGE_TYPES, HexIntegerField
)

import uuid


class GCM(Device):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	device_id = HexIntegerField(
			verbose_name=_('Device ID'), blank=True, null=True, db_index=True,
			help_text=_('ANDROID_ID / TelephonyManager.getDeviceId() (always as hex)')
	)
	registration_id = models.TextField(verbose_name=_('Registration ID'))
	cloud_message_type = models.CharField(
			verbose_name=_('Cloud Message Type'), max_length=3,
			choices=CLOUD_MESSAGE_TYPES, default='GCM',
			help_text=_('You should choose FCM or GCM')
	)
	objects = GCMDeviceManager()

	class Meta:
		verbose_name = _('GCM device')

	def send_message(self, message, **kwargs):
		from push_notifications.gcm import send_message as gcm_send_message

		data = kwargs.pop('extra', {})
		if message is not None:
			data['message'] = message

		return gcm_send_message(
				self.registration_id, data, self.cloud_message_type,
				application_id=self.application_id, **kwargs
		)


class APNS(Device):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	device_id = models.UUIDField(
			verbose_name=_('Device ID'), blank=True, null=True, db_index=True,
			help_text='UDID / UIDevice.identifierForVendor()'
	)
	registration_id = models.CharField(
			verbose_name=_('Registration ID'), max_length=200, unique=True
	)

	objects = APNSDeviceManager()

	class Meta:
		verbose_name = _('APNS device')

	def send_message(self, message, certfile=None, **kwargs):
		from push_notifications.apns import apns_send_message

		return apns_send_message(
				registration_id=self.registration_id,
				alert=message,
				application_id=self.application_id, certfile=certfile,
				**kwargs
		)


class WNS(Device):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	device_id = models.UUIDField(
			verbose_name=_('Device ID'), blank=True, null=True, db_index=True,
			help_text=_('GUID()')
	)
	registration_id = models.TextField(verbose_name=_('Notification URI'))

	objects = WNSDeviceManager()

	class Meta:
		verbose_name = _('WNS device')

	def send_message(self, message, **kwargs):
		from push_notifications.wns import wns_send_message

		return wns_send_message(
				uri=self.registration_id, message=message, application_id=self.application_id, **kwargs
		)


class WebPush(Device):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	registration_id = models.TextField(verbose_name=_('Registration ID'))
	p256dh = models.CharField(
			verbose_name=_('User public encryption key'),
			max_length=88)
	auth = models.CharField(
			verbose_name=_('User auth secret'),
			max_length=24)
	browser = models.CharField(
			verbose_name=_('Browser'), max_length=10,
			choices=BROWSER_TYPES, default=BROWSER_TYPES[0][0],
			help_text=_('Currently only support to Chrome, Firefox and Opera browsers')
	)
	objects = WebPushDeviceManager()

	class Meta:
		verbose_name = _('WebPush device')

	def send_message(self, message, **kwargs):
		from push_notifications.webpush import webpush_send_message

		return webpush_send_message(
				uri=self.registration_id, message=message, browser=self.browser,
				auth=self.auth, p256dh=self.p256dh, application_id=self.application_id, **kwargs)

	@property
	def device_id(self):
		return None
