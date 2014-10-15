# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0003_auto_20141015_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='assignment_base_dir',
            field=models.FilePathField(default=b'D:\\Code\\django-grader\\grader/assignments', allow_folders=True, allow_files=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='student_code_dir',
            field=models.FilePathField(default=b'D:\\Code\\django-grader\\grader/student_code', allow_folders=True, allow_files=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='use_gitlab',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userattempts',
            name='assignment',
            field=models.ForeignKey(default=1, to='course_management.Assignment'),
            preserve_default=False,
        ),
    ]
