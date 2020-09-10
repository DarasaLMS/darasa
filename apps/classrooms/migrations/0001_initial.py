# Generated by Django 3.0.8 on 2020-09-10 11:30

import apps.classrooms.models
import apps.classrooms.utils
from django.db import migrations, models
import sorl.thumbnail.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('room_id', models.IntegerField(default=apps.classrooms.models.Classroom.get_room_id, help_text='The room number which need to be unique.', unique=True, verbose_name='room number')),
                ('welcome_message', models.CharField(blank=True, help_text='Message which displayed on the chat window.', max_length=200, verbose_name='welcome message')),
                ('logout_url', models.URLField(default='http://localhost:4200', help_text='URL to which users will be redirected.', verbose_name='logout URL')),
                ('moderator_password', models.CharField(default=apps.classrooms.utils.get_random_password, max_length=120, verbose_name='moderator password')),
                ('attendee_password', models.CharField(default=apps.classrooms.utils.get_random_password, max_length=120, verbose_name='attendee password')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('cover', sorl.thumbnail.fields.ImageField(default='covers/default/cover.png', upload_to='covers/%Y/%m', verbose_name='cover image')),
                ('classroom_join_mode', models.CharField(choices=[('join_all', 'Join all clasrooms in this course'), ('choose_to_join', 'Choose to join a classroom')], default='join_all', max_length=32, verbose_name='classroom join mode')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('notes', models.FileField(blank=True, null=True, upload_to='notes/%Y/%m')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('category', models.CharField(choices=[('faq', 'Frequently Asked Questions (FAQ)'), ('announcement', 'Announcements')], default='announcement', max_length=32, verbose_name='category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('declined', 'Declined'), ('pending', 'Pending')], default='pending', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(blank=True, null=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
