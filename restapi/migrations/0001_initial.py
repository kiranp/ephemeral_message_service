# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=512)),
                ('timeout', models.PositiveIntegerField(default=60)),
                ('expiration_date', models.DateTimeField()),
            ],
        ),
    ]
