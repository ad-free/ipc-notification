# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from .models import Customer, Staff


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
	change_list_template = 'admin/users.html'
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'email',)}),
	)
	list_display = ('username', 'email', 'last_login', 'is_online',)
	list_filter = ['date_joined']
	exclude = ('groups',)
	readonly_fields = ('is_online',)

	def get_queryset(self, request):
		qs = super(CustomerAdmin, self).get_queryset(request)
		return qs.filter(is_staff=False, is_superuser=False)

	def save_model(self, request, obj, form, change):
		obj.is_staff = False
		obj.is_superuser = False
		obj.save()

	def get_server_info(self, obj):
		return mark_safe('<div style="display: none" class="server-info" data-host="{host}" data-port="{port}"></div>'.format(
				host=settings.API_QUEUE_HOST,
				port=settings.API_QUEUE_PORT
		))

	get_server_info.allow_tags = True

	class Media:
		static_url = getattr(settings, 'STATIC_URL')
		js = [
			static_url + 'assets/js/mqtt/mqttws31.js',
			static_url + 'assets/js/status.js',
		]


@admin.register(Staff)
class StaffAdmin(UserAdmin):
	fieldsets = (
		(None, {'fields': ('username', 'phone_number', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
		(_('Permissions'), {'fields': ('is_active', 'is_superuser', 'groups')}),
	)
	list_display = ('username', 'first_name', 'email', 'is_active', 'last_login')
	list_filter = ['is_active', 'date_joined', 'last_login']
	filter_horizontal = ('groups',)
	exclude = ('user_permissions',)

	def get_queryset(self, request):
		qs = super(StaffAdmin, self).get_queryset(request)
		return qs.filter(is_staff=True)

	def save_model(self, request, obj, form, change):
		obj.is_staff = True
		obj.save()
