# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.users.models import Customer


class Schedule(models.Model):
	serial = models.CharField(max_length=100)
	schedule = models.TextField(max_length=1024)
	is_active = models.BooleanField(default=False, verbose_name=_('Active'))
	user = models.ManyToManyField(Customer, related_name='schedule_user')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _('Schedule')
		verbose_name_plural = _('Schedules')

	def __str__(self):
		return self.serial

	def __unicode__(self):
		return u'{}'.format(self.serial)
