# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Customer(User):
	is_online = models.BooleanField(default=False, verbose_name=_('Online'))

	def __str__(self):
		return self.username

	def __unicode__(self):
		return u'{}'.format(self.username)
