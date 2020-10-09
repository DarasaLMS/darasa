# Generated by Django 3.0.8 on 2020-10-09 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20201009_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='color',
        ),
        migrations.AddField(
            model_name='school',
            name='copyright_text',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='school',
            name='primary_color',
            field=models.CharField(blank=True, max_length=10, verbose_name='primary color'),
        ),
        migrations.AddField(
            model_name='school',
            name='secondary_color',
            field=models.CharField(blank=True, max_length=10, verbose_name='secondary color'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.School'),
        ),
        migrations.AlterField(
            model_name='school',
            name='moto',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
