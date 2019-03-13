# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from apps.apis.serializers import (
	RegisterSerializer, UpdateSerializer, DeleteSerializer,
	SendSerializer, ActiveSerializer
)


class RegisterViewSet(viewsets.ModelViewSet):
	""" Register account """
	serializer_class = RegisterSerializer
	http_method_names = ['post']


class UpdateViewSet(viewsets.ModelViewSet):
	""" Update account """
	serializer_class = UpdateSerializer
	http_method_names = ['post']


class DeleteViewSet(viewsets.ModelViewSet):
	""" Delete schedule or account """
	serializer_class = DeleteSerializer
	http_method_names = ['post']


class ActiveViewSet(viewsets.ModelViewSet):
	""" Active or De-active schedule"""
	serializer_class = ActiveSerializer
	http_method_names = ['post']


class SendViewSet(viewsets.ModelViewSet):
	""" Send a notification to user """
	serializer_class = SendSerializer
	http_method_names = ['post']
