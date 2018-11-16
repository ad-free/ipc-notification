# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..apis.utils import APIAccessPermission, message_format, push_notification
from ..commons.utils import logger_format

from functools import partial

import time
import logging

logger = logging.getLogger('')


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_push_notification'),))
def api_push_notification(request):
	logger.info(logger_format('<-------  START  ------->', api_push_notification.__name__))
	errors = {}
	platform = request.POST.get('platform', '').strip()
	token = request.POST.get('token', '').strip()
	bundle = request.POST.get('bundle', '').strip()

	logger.info(logger_format('Check platform', api_push_notification.__name__))
	if not platform:
		errors.update({'platform': _('This field is required.')})
	logger.info(logger_format('Check token', api_push_notification.__name__))
	if not token:
		errors.update({'token': _('This field is required.')})
	logger.info(logger_format('Check bundle', api_push_notification.__name__))
	if not bundle:
		errors.update({'bundle': _('This field is required.')})

	logger.info(logger_format('Check the parameters include platform, token and bundle', api_push_notification.__name__))
	if not errors:
		logger.info(logger_format('Check bundle list', api_push_notification.__name__))
		if platform in settings.BUNDLE_LIST.keys() and bundle in settings.BUNDLE_LIST[platform]:
			message = message_format(
				title='This is a title',
				body='This is content message',
				url='http://cmr.iotc.vn/inbox/1',
				inbox_id=1,
				time=time.time(),
				serial='ds4x8z4xcajcw'
			)
			response = push_notification(platform, bundle, token, message)
			if response:
				logger.info(logger_format('<-------  END  ------->', api_push_notification.__name__))
				return Response({
					'status': status.HTTP_200_OK,
					'result': True
				}, status=status.HTTP_200_OK)
			else:
				errors.update({'message': _('Unable to send notification, please try again.')})
		else:
			errors.update({'message': _('Check out your mobile platform')})

	logger.info(logger_format('<-------  START  ------->', api_push_notification.__name__))
	return Response({
		'status': status.HTTP_400_BAD_REQUEST,
		'result': False,
		'errors': errors
	}, status=status.HTTP_200_OK)
