from django.urls import path
from django.contrib.auth.decorators import login_required

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.apis import views

docs = get_schema_view(
		openapi.Info(
				title='Snippets API',
				default_version='v1.0',
				description='',
				terms_of_service='',
				contact=openapi.Contact(email='duyta8@fpt.com.vn')
		),
		public=True,
		permission_classes=(permissions.IsAuthenticated, permissions.IsAdminUser),
)

re_doc = get_schema_view(
		openapi.Info(
				title='Snippets API',
				default_version='v1.0',
				description='',
				terms_of_service='',
				contact=openapi.Contact(email='duyta8@fpt.com.vn')
		),
		public=True,
		permission_classes=(permissions.IsAuthenticated, permissions.IsAdminUser),
)

urlpatterns = [
	# Docs
	path('docs/', login_required(docs.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
	path('redoc/', login_required(re_doc.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
	# APIs
	path('auth/sign-in/', views.api_auth_sign_in, name='api_auth_sign_in'),
	path('auth/sign-out/', views.api_auth_sign_out, name='api_auth_sign_out'),
	path('notification/register/', views.api_notification_register, name='api_notification_register'),
	path('notification/update/', views.api_notification_update, name='api_notification_update'),
	path('notification/delete/', views.api_notification_delete, name='api_notification_delete'),
	path('notification/active/', views.api_notification_active, name='api_notification_active'),
	path('notification/send/', views.api_notification_send, name='api_notification_send'),
]
