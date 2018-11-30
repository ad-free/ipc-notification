# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
	fields = ('serial', 'user', 'schedule', 'is_active')
	list_display = ('serial', 'is_active')
	filter_horizontal = ('user',)
	search_fields = ('serial',)
	list_filter = ('is_active',)
	ordering = ['serial']
