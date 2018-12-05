from django.urls import path
from apps.apis import views

urlpatterns = [
	path('notification/register/', views.api_notification_register, name='api_notification_register'),
	path('notification/update/', views.api_notification_update, name='api_notification_update'),
	path('notification/delete/', views.api_notification_delete, name='api_notification_delete'),
	path('notification/active/', views.api_notification_active, name='api_notification_active'),
]
