# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.users_auth.models import User


class Customer(User):
	is_online = models.BooleanField(default=False, verbose_name=_('Online'))
