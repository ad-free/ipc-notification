# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..apis.utils import APIAccessPermission
from ..commons.utils import check_special_chars, logger_format

from functools import partial

import logging

logger = logging.getLogger('')


@api_view(['POST'])
@permission_classes((partial(APIAccessPermission, 'api_push_notification'),))
def api_push_notification(request):
	return Response()
