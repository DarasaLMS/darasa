# Generated by Django 3.0.8 on 2020-08-10 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0002_auto_20200807_1035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classroom',
            name='groups',
        ),
        migrations.DeleteModel(
            name='ClassroomGroup',
        ),
    ]
