# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-23 14:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlb_proxy', '0008_auto_20180404_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clustermember',
            name='is_alive',
            field=models.IntegerField(choices=[(0, '等待被master接受'), (1, '状态正常'), (2, '状态异常')], default=0, verbose_name='是否存活'),
        ),
        migrations.AlterField(
            model_name='clustermember',
            name='is_init',
            field=models.IntegerField(choices=[(0, '未初始化'), (1, '已初始化')], default=0, verbose_name='是否初始化'),
        ),
    ]
