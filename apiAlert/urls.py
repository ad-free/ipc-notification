"""apiNotifications URL Configuration"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
	path('', admin.site.urls),
	path('api/v2/', include('apps.apis.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Notifications - System Administration'
admin.site.index_title = 'FPT Notifications System'
admin.site.site_title = 'FPT'

if 'django_prometheus' in settings.INSTALLED_APPS:
	urlpatterns += [path('', include('django_prometheus.urls'))]
