# Generated by Django 2.1.3 on 2018-12-11 00:48

import apps.users_auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
            ],
            options={
                'verbose_name': 'Staff account',
                'verbose_name_plural': 'Staff accounts',
                'proxy': True,
                'indexes': [],
            },
            bases=('users.customer',),
            managers=[
                ('objects', apps.users_auth.models.UserManager()),
            ],
        ),
    ]
