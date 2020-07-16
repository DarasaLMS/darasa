# Generated by Django 3.0.8 on 2020-07-16 18:47

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classrooms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message', models.TextField(blank=True)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('classroom', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='classrooms.Classroom')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user_feedback', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_user_feedback', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedback',
                'unique_together': {('from_user', 'to_user', 'classroom')},
            },
        ),
    ]
