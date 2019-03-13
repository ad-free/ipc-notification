from django.urls import path, include
from apps.apis import views
from apps.apis import viewset
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='API Lists')

routers = routers.DefaultRouter()
routers.register(r'notification/register', viewset.RegisterViewSet, basename='register')
routers.register(r'notification/update', viewset.UpdateViewSet, basename='update')
routers.register(r'notification/active', viewset.ActiveViewSet, basename='active')
routers.register(r'notification/delete', viewset.DeleteViewSet, basename='delete')
routers.register(r'notification/send', viewset.SendViewSet, basename='send')

urlpatterns = [
	# Docs
	path('', include(routers.urls)),
	path('docs', schema_view),
	path('notification/register/', views.api_notification_register, name='api_notification_register'),
	path('notification/update/', views.api_notification_update, name='api_notification_update'),
	path('notification/delete/', views.api_notification_delete, name='api_notification_delete'),
	path('notification/active/', views.api_notification_active, name='api_notification_active'),
	path('notification/send/', views.api_notification_send, name='api_notification_send'),
]
