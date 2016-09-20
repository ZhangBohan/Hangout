# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-20 15:15
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0007_photo_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='url',
            field=django.contrib.postgres.fields.jsonb.JSONField(help_text='URL', verbose_name='URL'),
        ),
    ]
