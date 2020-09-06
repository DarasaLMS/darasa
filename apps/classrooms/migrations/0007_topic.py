# Generated by Django 3.0.8 on 2020-09-03 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0006_auto_20200813_2241'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('notes', models.FileField(blank=True, null=True, upload_to='notes/%Y/%m')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='classrooms.Course', verbose_name='course')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classrooms.Topic')),
            ],
        ),
    ]