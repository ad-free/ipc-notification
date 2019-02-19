# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def server_info(name):
	if name == 'host':
		return getattr(settings, 'API_QUEUE_HOST', '')
	elif name == 'port':
		return getattr(settings, 'API_QUEUE_WEBSOCKET_PORT', '')
	elif name == 'ssl':
		return getattr(settings, 'API_QUEUE_SSL', '')
	elif name == 'topic':
		return getattr(settings, 'USER_TOPIC_STATUS', '')
	return ''
