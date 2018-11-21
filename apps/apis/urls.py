from django.urls import path
from apps.apis import views

urlpatterns = [
	path('notification/register/', views.api_notification_register, name='api_notification_register'),
	path('notification/update/', views.api_notification_update, name='api_notification_update'),
	path('notification/push/', views.api_notification_push, name='api_notification_push'),
]
