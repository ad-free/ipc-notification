# Generated by Django 2.1.3 on 2018-12-03 11:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='user',
            field=models.ManyToManyField(blank=True, related_name='schedule_customer', to=settings.AUTH_USER_MODEL),
        ),
    ]
