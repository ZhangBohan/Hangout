# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-16 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hangout', '0005_auto_20161115_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='accepted_count',
            field=models.IntegerField(default=1, help_text='已接受人数', verbose_name='已接受人数'),
        ),
    ]