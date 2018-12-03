# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminTimeWidget

from .models import Schedule


class TimeForm(forms.ModelForm):
	start_time = forms.TimeField(widget=AdminTimeWidget(format=settings.TIME_FORMAT), required=False)
	end_time = forms.TimeField(widget=AdminTimeWidget(format=settings.TIME_FORMAT), required=False)

	class Meta:
		model = Schedule
		fields = '__all__'
