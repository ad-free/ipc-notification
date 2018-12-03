# Generated by Django 2.1.3 on 2018-12-03 11:22

from django.db import migrations, models
import push_notifications.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APNS',
            fields=[
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('active', models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('application_id', models.CharField(blank=True, help_text='Opaque application identity, should be filled in for multiple key/certificate access', max_length=64, null=True, verbose_name='Application ID')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.UUIDField(blank=True, db_index=True, help_text='UDID / UIDevice.identifierForVendor()', null=True, verbose_name='Device ID')),
                ('registration_id', models.CharField(max_length=200, unique=True, verbose_name='Registration ID')),
            ],
            options={
                'verbose_name': 'APNS device',
            },
        ),
        migrations.CreateModel(
            name='GCM',
            fields=[
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('active', models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('application_id', models.CharField(blank=True, help_text='Opaque application identity, should be filled in for multiple key/certificate access', max_length=64, null=True, verbose_name='Application ID')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False)),
                ('device_id', push_notifications.fields.HexIntegerField(blank=True, db_index=True, help_text='ANDROID_ID / TelephonyManager.getDeviceId() (always as hex)', null=True, verbose_name='Device ID')),
                ('registration_id', models.TextField(verbose_name='Registration ID')),
                ('cloud_message_type', models.CharField(choices=[('FCM', 'Firebase Cloud Message'), ('GCM', 'Google Cloud Message')], default='GCM', help_text='You should choose FCM or GCM', max_length=3, verbose_name='Cloud Message Type')),
            ],
            options={
                'verbose_name': 'GCM device',
            },
        ),
        migrations.CreateModel(
            name='WebPush',
            fields=[
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('active', models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('application_id', models.CharField(blank=True, help_text='Opaque application identity, should be filled in for multiple key/certificate access', max_length=64, null=True, verbose_name='Application ID')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False)),
                ('registration_id', models.TextField(verbose_name='Registration ID')),
                ('p256dh', models.CharField(max_length=88, verbose_name='User public encryption key')),
                ('auth', models.CharField(max_length=24, verbose_name='User auth secret')),
                ('browser', models.CharField(choices=[('CHROME', 'Chrome'), ('FIREFOX', 'Firefox'), ('OPERA', 'Opera')], default='CHROME', help_text='Currently only support to Chrome, Firefox and Opera browsers', max_length=10, verbose_name='Browser')),
            ],
            options={
                'verbose_name': 'WebPush device',
            },
        ),
        migrations.CreateModel(
            name='WNS',
            fields=[
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('active', models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('application_id', models.CharField(blank=True, help_text='Opaque application identity, should be filled in for multiple key/certificate access', max_length=64, null=True, verbose_name='Application ID')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.UUIDField(blank=True, db_index=True, help_text='GUID()', null=True, verbose_name='Device ID')),
                ('registration_id', models.TextField(verbose_name='Notification URI')),
            ],
            options={
                'verbose_name': 'WNS device',
            },
        ),
    ]
