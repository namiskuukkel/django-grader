# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='execution_timeout',
            field=models.PositiveIntegerField(default=15),
            preserve_default=True,
        ),
    ]
