# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Schedule
from .forms import TimeForm


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
	form = TimeForm
	fields = ('serial', 'date', 'start_time', 'end_time', 'repeat_at', 'user', 'repeat_status', 'is_active')
	list_display = ('serial', 'schedule_id', 'date', 'start_time', 'end_time', 'repeat_status', 'is_active')
	filter_horizontal = ('user',)
	search_fields = ('serial',)
	list_filter = ('repeat_status', 'is_active',)
	ordering = ['serial']
