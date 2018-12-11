# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Customer, Staff


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'is_online')}),
	)
	list_display = ('username', 'email', 'is_online', 'last_login')
	list_filter = ['is_online', 'date_joined']
	exclude = ('groups',)

	def get_queryset(self, request):
		qs = super(CustomerAdmin, self).get_queryset(request)
		return qs.filter(is_staff=False, is_superuser=False)

	def save_model(self, request, obj, form, change):
		obj.is_staff = False
		obj.is_superuser = False
		obj.save()


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
