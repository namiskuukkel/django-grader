# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0002_assignment_execution_timeout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='contact',
            field=models.EmailField(max_length=75),
        ),
    ]
