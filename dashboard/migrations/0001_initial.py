# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=255, unique=True)),
                ('date_of_birth', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('number', models.IntegerField(verbose_name='Mobile Number', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name_of_plan', models.CharField(verbose_name='Plan name', max_length=50)),
                ('credits', models.IntegerField(verbose_name='Credits')),
                ('price', models.IntegerField(verbose_name='Price')),
                ('duration', models.CharField(verbose_name='Validity', max_length=30)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_Plan',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('started_on', models.DateField(verbose_name='Subscribed On', auto_now_add=True)),
                ('paid_amount', models.IntegerField(default=0, verbose_name='Paid Amount')),
                ('total_credits', models.IntegerField(verbose_name='Total Credits')),
                ('used_credits', models.IntegerField(verbose_name='Used Credits')),
                ('remaining_credits', models.IntegerField(verbose_name='Remaining Credits')),
                ('ending_on', models.DateField(verbose_name='Valid Upto', auto_now_add=True)),
                ('plan', models.ForeignKey(to='dashboard.Plan')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WhatApp_Message_Format',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('sent_on', models.DateField(verbose_name='Sent On', auto_now_add=True)),
                ('msg_text', models.CharField(verbose_name='message', max_length=1500, blank=True, null=True)),
                ('from_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WhatsApp_Bulk_Message',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('delivered', models.BooleanField(default=False)),
                ('message_format', models.ForeignKey(to='dashboard.WhatApp_Message_Format')),
                ('to_contact', models.ForeignKey(to='dashboard.Contact')),
            ],
        ),
    ]
