# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0004_auto_20141015_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='assignment_base_dir',
            field=models.FilePathField(allow_folders=True, allow_files=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='student_code_dir',
            field=models.FilePathField(allow_folders=True, allow_files=False),
        ),
    ]
