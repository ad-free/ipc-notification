API_ALERT_PROTOCOL = 'http'
# API_ALERT_PROTOCOL = 'https'
# API_ALERT_HOST = 'prod-alert.iotc.vn'
API_ALERT_HOST = '192.168.2.132'
API_ALERT_PORT = 8000
API_ALERT_LIST = {
	'register': '{protocol}://{host}:{port}/api/v2/notification/register/',
	'delete': '{protocol}://{host}:{port}/api/v2/notification/delete/',
	'active': '{protocol}://{host}:{port}/api/v2/notification/active/',
	'update': '{protocol}://{host}:{port}/api/v2/notification/update/',
}
# API_ALERT_GIS = 'c7391475ec5b400b8884655fe0cdb54a'
API_ALERT_GIS = 'c7391475ec5b400b8884655fe0cdb54a'