# Generated by Django 3.0.8 on 2020-10-06 17:16

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20201006_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='about',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='terms_and_privacy',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
    ]