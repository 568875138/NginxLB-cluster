# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-05-16 16:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nlb_proxy', '0019_auto_20180514_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesscontroliplist',
            name='add_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_accessips', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='blackliststrategy',
            name='proxy_domain_name',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blacklist_refers', to='nlb_proxy.HttpProxy'),
        ),
        migrations.AlterField(
            model_name='whiteliststrategy',
            name='proxy_domain_name',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='whitelist_refers', to='nlb_proxy.HttpProxy'),
        ),
    ]
