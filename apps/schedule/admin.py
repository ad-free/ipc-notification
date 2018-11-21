# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
	fields = ('user', 'serial', 'schedule', 'is_active')
	list_display = ('user', 'serial', 'is_active')
	search_fields = ('user', 'serial')
	list_filter = ('is_active',)
	ordering = ['user', 'serial']
