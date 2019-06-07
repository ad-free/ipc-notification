# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import os
import ssl

ALLOWED_HOSTS = ['192.168.2.69', '127.0.0.1']

DEBUG = True

TIME_ZONE = 'Asia/Ho_Chi_Minh'
TIME_FORMAT = '%H:%M'

# DATETIME Format
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

PUSH_NOTIFICATIONS_SETTINGS = {
	'UPDATE_ON_DUPLICATE_REG_ID': True,
	'FCM_API_KEY': 'AAAA7kxsNIg:APA91bELQ3wnZ3ObKCBi-ojaSrbaMw6Nx1AXJaZBNpQUSUcuP_CfC3wDQGakeTER9zPyfGXVRhz5Rn4kr8N1sbxqfSlkYmzfhjiEAJ_grPXPOaG314IOCYT5W1LTu7VvpZ5um9ILJNO4',
	'APNS_CERTIFICATE': os.path.join('certificate/apns/prod_cmr.pem'),
	'APNS_TOPIC': 'cmr.iotc.vn',
	'APNS_USE_ALTERNATIVE_PORT': False,
	'APNS_USE_SANDBOX': True
}

# Config SSL
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Queue System Info
API_QUEUE_HOST = 'prod-queue.iotc.vn'
API_QUEUE_PORT = 1883
API_QUEUE_WEBSOCKET_PORT = 9001
API_QUEUE_SSL = False
# API_QUEUE_HOST = 'test.mosquitto.org'
# API_QUEUE_WEBSOCKET_PORT = 8081
CA_ROOT_CERT_FILE = os.path.join('certificate/mqtt/ca.crt')
CA_ROOT_CERT_KEY = None
CA_ROOT_CERT_CLIENT = None
CA_ROOT_CERT_REQS = ssl.CERT_NONE
CA_ROOT_CERT_CIPHERS = None
CA_ROOT_TLS_VERSION = ssl.PROTOCOL_TLSv1_2
API_ALERT_USERNAME = 'notify'
API_ALERT_PASSWORD = 'abcd@123456'
MQTT_TIMEOUT = 3
MQTT_PREFIXES = 'ipc'

# TOPIC DEFINE
USER_TOPIC_LOG = 'user/{name}/data/log'
USER_TOPIC_ANNOUNCE = 'user/{name}/data/announce'
USER_TOPIC_STATUS = 'user/{name}/status'
CAMERA_TOPIC_STATUS = 'device/{name}/status'
CAMERA_TOPIC_DATA = 'device/{name}/data/announce'
CAMERA_TOPIC_ALARM = 'ipc/{name}/alarm'
WOWZA_TOPIC_STATUS = 'wz/{name}/stream/status'
SUBSCRIBE_TOPICS = [
	USER_TOPIC_STATUS,
	USER_TOPIC_LOG,
	CAMERA_TOPIC_ALARM,
	WOWZA_TOPIC_STATUS
]

# DJANGO PROMETHEUS
settings.INSTALLED_APPS += ['django_prometheus']
PROMETHEUS_BEGIN = ['django_prometheus.middleware.PrometheusBeforeMiddleware']
PROMETHEUS_END = ['django_prometheus.middleware.PrometheusAfterMiddleware']
settings.MIDDLEWARE = PROMETHEUS_BEGIN + settings.MIDDLEWARE + PROMETHEUS_END

LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'verbose': {
			'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
			'datefmt': "%d/%b/%Y %H:%M:%S"
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
	},
	'handlers': {
		'file': {
			'level': 'INFO',
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'filename': os.path.join(settings.MEDIA_ROOT, 'logs', 'api.log'),
			'when': 'D',
			'interval': 1,
			'backupCount': 10,
			'formatter': 'verbose'
		},
	},
	'loggers': {
		'': {
			'handlers': ['file'],
			'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO')
		}
	}
}

ADMIN_REORDER = (
	{'app': 'apis', 'models': (
		{'model': 'apis.Feature', 'label': _('Features')},
		{'model': 'apis.Registration', 'label': _('Registrations')},
	)},
	{'app': 'users', 'label': 'Authentication and Authorization', 'models': (
		{'model': 'users.Staff', 'label': _('Staff accounts')},
	)},
	{'app': 'users', 'label': 'Users', 'models': (
		{'model': 'users.Customer', 'label': _('Customer accounts')},
	)},
	{'app': 'notifications', 'label': _('Devices Management'), 'models': (
		{'model': 'notifications.APNS', 'label': _('APNSDevice')},
		{'model': 'notifications.GCM', 'label': _('GCMDevice')},
		{'model': 'notifications.WNS', 'label': _('WNSDevice')},
		{'model': 'notifications.WebPush', 'label': _('WebPushDevice')},
	)},
	{'app': 'schedule', 'label': _('Schedule'), 'models': (
		{'model': 'schedule.Schedule', 'label': _('Schedules')},
	)}
)

DATABASES = {
	'default': {
		'ENGINE': 'apps.mongolink',
		'NAME': 'db_alert',
		# 'USER': '',
		# 'PASSWORD': '',
		# 'HOST': '118.69.135.186',
		'HOST': '127.0.0.1',
		'PORT': 27017
	}
}

LOGIN_URL = 'http://192.168.2.69:8000/login/?next=/'
LOGOUT_URL = 'http://192.168.2.69:8000/logout'

SWAGGER_SETTINGS = {
	'SECURITY_DEFINITIONS': {
		'GIS': {
			'type': 'apiKey',
			'in': 'header',
			'name': 'gis'
		}
	},
	'USE_SESSION_AUTH': True,
	'LOGIN_URL': LOGIN_URL,
	'LOGOUT_URL': LOGOUT_URL,
	'SUPPORTED_SUBMIT_METHODS': [
		'get',
		'post',
		'put',
		'delete',
		'options',
		'head',
		'path',
		'trace'
	],
	'REFETCH_SCHEMA_WITH_AUTH': True,  # Default: False
	'REFETCH_SCHEMA_ON_LOGOUT': True,  # Default: False
	'FETCH_SCHEMA_WITH_QUERY': True,  # Default: False
	'OPERATIONS_SORTER': 'method',  # None, alpha, method
	'DOC_EXPANSION': 'list',  # none, list, full
	'NATIVE_SCROLLBARS': True,  # Default: False
}

REDOC_SETTINGS = {
	'LAZY_RENDERING': True,
	'EXPAND_RESPONSES': True
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

if DEBUG and os.environ.get('RUN_MAIN', None) != 'true':
	LOGGING = {}
