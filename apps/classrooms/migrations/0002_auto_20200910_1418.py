# Generated by Django 3.0.8 on 2020-09-10 11:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timetable', '0001_initial'),
        ('accounts', '0001_initial'),
        ('classrooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentattendance',
            name='occurrence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.Occurrence', verbose_name='occurrence'),
        ),
        migrations.AddField(
            model_name='studentattendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Student', verbose_name='student'),
        ),
        migrations.AddField(
            model_name='request',
            name='classrooms',
            field=models.ManyToManyField(blank=True, help_text='Preferred classrooms to join', to='classrooms.Classroom'),
        ),
        migrations.AddField(
            model_name='request',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classrooms.Course'),
        ),
        migrations.AddField(
            model_name='request',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_classrooms_request_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_classrooms_request_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Student'),
        ),
        migrations.AddField(
            model_name='request',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Teacher'),
        ),
        migrations.AddField(
            model_name='post',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='classrooms.Course', verbose_name='course'),
        ),
        migrations.AddField(
            model_name='post',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_classrooms_post_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_classrooms_post_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='parent_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classrooms.Post'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='classrooms.Course', verbose_name='course'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_classrooms_lesson_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lesson',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_classrooms_lesson_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lesson',
            name='parent_lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classrooms.Lesson'),
        ),
        migrations.AddField(
            model_name='course',
            name='assistant_teachers',
            field=models.ManyToManyField(blank=True, related_name='assistant_teachers', to='accounts.Teacher', verbose_name='assistant teachers'),
        ),
        migrations.AddField(
            model_name='course',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_classrooms_course_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='educational_stages',
            field=models.ManyToManyField(blank=True, to='accounts.EducationalStage', verbose_name='educational stages'),
        ),
        migrations.AddField(
            model_name='course',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_classrooms_course_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, to='accounts.Student', verbose_name='students'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teacher', to='accounts.Teacher', verbose_name='teacher'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='classrooms', to='classrooms.Course', verbose_name='course'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_classrooms_classroom_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classroom',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_classrooms_classroom_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='request',
            unique_together={('student', 'course')},
        ),
    ]
