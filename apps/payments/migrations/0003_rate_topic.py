# Generated by Django 3.0.8 on 2020-07-21 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0002_remove_request_cancelled'),
        ('payments', '0002_auto_20200721_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classrooms.Topic'),
        ),
    ]