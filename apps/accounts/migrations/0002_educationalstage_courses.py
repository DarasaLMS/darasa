# Generated by Django 3.0.8 on 2020-08-07 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classrooms', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationalstage',
            name='courses',
            field=models.ManyToManyField(to='classrooms.Course'),
        ),
    ]
