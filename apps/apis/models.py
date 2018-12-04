# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

import uuid

STATUS_CHOICES = (
	(True, _('Active')),
	(False, _('Inactive'))
)

APP_TYPE_CHOICES = (
	('ios', _('iOS')),
	('android', _('Android')),
	('web', _('Website'))
)


class Feature(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=100, unique=True)
	type = models.CharField(max_length=100)
	brief = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.CharField(max_length=150, null=True)
	modified_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '[{}] {}'.format(self.type, self.name)

	def __unicode__(self):
		return u'[{}] {}'.format(self.type, self.name)


class Registration(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	app_package = models.CharField(max_length=200, verbose_name=_('Package'))
	app_id = models.CharField(unique=True, max_length=50, null=True, verbose_name=_('ID'))
	app_type = models.CharField(max_length=200, verbose_name=_('Type'), choices=APP_TYPE_CHOICES)
	server = models.BooleanField(default=1, help_text=_(u'Provide server account to this user'), verbose_name=_('Server status'))
	features = models.ManyToManyField(Feature, related_name='registration_features')
	status = models.BooleanField(default=1, choices=STATUS_CHOICES)
	created_by = models.CharField(max_length=150, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return u'{}'.format(self.app_package)

	def __unicode__(self):
		return u'{}'.format(self.app_package)

	def save(self, *args, **kwargs):
		if not self.app_id:
			self.app_id = uuid.uuid4().hex
		super(Registration, self).save(*args, **kwargs)
