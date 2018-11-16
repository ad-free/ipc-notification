from django.urls import path
from apps.apis import views

urlpatterns = [
	path('push-notification/', views.api_push_notification, name='api_push_notification'),
]
