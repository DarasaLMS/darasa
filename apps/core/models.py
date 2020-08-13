import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="created_%(app_label)s_%(class)s_set",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="modified_%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True
