"""
WSGI config for apiAlert project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apiAlert.settings')
os.environ['prometheus_multiproc_dir'] = os.path.join('prometheus')

application = get_wsgi_application()
