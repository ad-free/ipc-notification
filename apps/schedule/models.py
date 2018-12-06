# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from apps.users.models import Customer

import uuid


class Schedule(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	user = models.ManyToManyField(Customer, blank=True, related_name='schedule_customer')
	schedule_id = models.UUIDField(editable=False)
	serial = models.CharField(max_length=100)
	start_time = models.TimeField(default=now, blank=True, null=True)
	end_time = models.TimeField(default=now, blank=True, null=True)
	date = models.DateField(blank=True, null=True)
	repeat_at = models.CharField(max_length=255, blank=True, null=True)
	repeat_status = models.BooleanField(default=False)
	is_active = models.BooleanField(default=False, verbose_name=_('Active'))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = (('schedule_id', 'serial'),)
		verbose_name = _('Schedule')
		verbose_name_plural = _('Schedules')

	def save(self, *args, **kwargs):
		if not self.schedule_id:
			self.schedule_id = uuid.uuid1().hex
		return super(Schedule, self).save(*args, **kwargs)

	def __str__(self):
		return self.serial

	def __unicode__(self):
		return u'{}'.format(self.serial)
