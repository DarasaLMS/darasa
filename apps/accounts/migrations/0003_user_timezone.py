# Generated by Django 3.0.8 on 2021-01-17 15:19

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201125_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='Africa/Nairobi'),
        ),
    ]
