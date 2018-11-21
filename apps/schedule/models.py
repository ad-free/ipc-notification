# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Schedule(models.Model):
	user = models.CharField(max_length=100)
	serial = models.CharField(max_length=100)
	schedule = models.TextField(max_length=1024)
	is_active = models.BooleanField(default=False, verbose_name=_('Active'))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _('Schedule')
		verbose_name_plural = _('Schedules')

	def __str__(self):
		return self.user

	def __unicode__(self):
		return u'{}'.format(self.user)
