# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Customer
from .forms import UserAdminCreationForm, UserAdminChangeForm


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
	form = UserAdminChangeForm
	add_form = UserAdminCreationForm
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'email',)}),
		(_('Permissions and Status'), {'fields': ('is_staff', 'is_superuser', 'is_online', 'is_active',)}),
	)
	add_fieldsets = (
		(None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2')}),
	)
	list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'last_login')
	list_filter = ['is_active', 'date_joined', 'last_login']
	exclude = ('user_permissions',)
