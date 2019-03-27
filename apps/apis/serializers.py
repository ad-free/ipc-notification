# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

LETTER_TYPE = (
	(201, 'Payment system'),
	(202, 'Camera Notification'),
	(203, 'Camera Change Owner'),
	(204, 'Gift code Sending'),
)

NOTIFICATION_TYPE = (
	(101, 'Camera motion'),
	(102, 'User Inbox'),
)


class RegisterSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=32, required=True)
	password = serializers.CharField(max_length=255, required=True)
	platform = serializers.CharField(max_length=255, required=True)
	device_token = serializers.CharField(max_length=255, required=True)
	bundle = serializers.CharField(max_length=100, required=True)

	def create(self, validated_data):
		pass

	def update(self, instance, validated_data):
		pass


class UpdateSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=32, required=True)
	new_username = serializers.CharField(max_length=32, required=False, allow_blank=True, allow_null=True)
	serial = serializers.CharField(max_length=32, required=False)
	schedule = serializers.CharField(max_length=255, required=False)
	is_unshared = serializers.CharField(max_length=50, required=False)

	def create(self, validated_data):
		pass

	def update(self, instance, validated_data):
		pass


class DeleteSerializer(serializers.Serializer):
	serial = serializers.CharField(max_length=32, required=True)
	schedule_id = serializers.CharField(max_length=255, required=True)
	is_delete = serializers.IntegerField(default=0, required=False)

	def create(self, validated_data):
		pass

	def update(self, instance, validated_data):
		pass


class ActiveSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=32, required=True)
	serial = serializers.CharField(max_length=32, required=True)
	schedule_id = serializers.CharField(max_length=255, required=True)
	is_active = serializers.IntegerField(default=0, required=False)

	def create(self, validated_data):
		pass

	def update(self, instance, validated_data):
		pass


class SendSerializer(serializers.Serializer):
	acm_id = serializers.UUIDField(required=True)
	phone_number = serializers.CharField(max_length=30, required=True)
	title = serializers.CharField(max_length=100, required=True)
	body = serializers.CharField(max_length=1024, required=True)
	letter_type = serializers.IntegerField(required=True)
	attachment = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
	notification_title = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
	notification_body = serializers.CharField(max_length=1024, required=False, allow_blank=True, allow_null=True)
	notification_type = serializers.IntegerField(required=True)

	def create(self, validated_data):
		pass

	def update(self, instance, validated_data):
		pass
