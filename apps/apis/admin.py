# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from apps.apis.models import Registration, Feature


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
	fields = ('name', 'type', 'brief')
	list_display = ('name', 'type', 'brief', 'created_at', 'modified_at')
	search_fields = ('name', 'type')
	# date_hierarchy = 'created_at'
	ordering = ['name']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
	list_display = ('app_package', 'app_id', 'app_type', 'status', 'created_by', 'created_at')
	filter_horizontal = ('features',)
	search_fields = ('app_package', 'app_id')
	# date_hierarchy = 'created_at'

	def get_form(self, request, obj=None, **kwargs):
		if obj is None:
			kwargs['fields'] = ('app_package', 'app_type', 'features', 'server', 'status')
		else:
			kwargs['fields'] = ('app_package', 'app_id', 'app_type', 'server', 'features', 'status')
		return super(RegistrationAdmin, self).get_form(request, obj, **kwargs)

	def save_model(self, request, obj, form, change):
		if not obj.created_by:
			obj.created_by = request.user.username
		obj.save()
