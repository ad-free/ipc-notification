# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.users_auth.models import User


class Customer(User):
	is_online = models.BooleanField(default=False, verbose_name=_('Online'))


class Staff(Customer):
	class Meta:
		proxy = True
		verbose_name = _('Staff account')
		verbose_name_plural = _('Staff accounts')
