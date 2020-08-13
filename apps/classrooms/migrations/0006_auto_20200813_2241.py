# Generated by Django 3.0.8 on 2020-08-13 19:41

import apps.classrooms.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200813_2241'),
        ('classrooms', '0005_course_educational_stages'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='classroom_join_mode',
            field=models.CharField(choices=[('join_all', 'Join all clasrooms in this course'), ('choose_to_join', 'Choose to join a classroom')], default='join_all', max_length=32, verbose_name='classroom join mode'),
        ),
        migrations.AddField(
            model_name='request',
            name='classrooms',
            field=models.ManyToManyField(blank=True, help_text='Preferred classrooms to join', to='classrooms.Classroom'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='attendee_password',
            field=models.CharField(default=apps.classrooms.utils.get_random_password, max_length=120, verbose_name='attendee password'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='logout_url',
            field=models.URLField(default='http://localhost:4200', help_text='URL to which users will be redirected.', verbose_name='logout URL'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='moderator_password',
            field=models.CharField(default=apps.classrooms.utils.get_random_password, max_length=120, verbose_name='moderator password'),
        ),
        migrations.AlterField(
            model_name='course',
            name='educational_stages',
            field=models.ManyToManyField(blank=True, to='accounts.EducationalStage', verbose_name='educational stages'),
        ),
        migrations.AlterField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, to='accounts.Student', verbose_name='students'),
        ),
    ]
