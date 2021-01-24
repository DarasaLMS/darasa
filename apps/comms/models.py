import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.core.models import BaseModel
from apps.accounts.models import User


class Message(BaseModel):
    FEEDBACK = "feedback"
    RATING = "rating"
    CHAT = "chat"
    CATEGORIES = ((FEEDBACK, _("Feedback")), (RATING, _("Rating")), (CHAT, _("Chat")))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        _("category"), max_length=16, choices=CATEGORIES, default=FEEDBACK
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="from_user_message",
        verbose_name=_("from"),
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="to_user_message",
        verbose_name=_("to"),
        null=True,
        blank=True,
    )
    title = models.CharField(_("title"), max_length=64)
    description = models.TextField(_("description"), blank=True)
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children_messages",
    )
    rating = models.PositiveSmallIntegerField(
        _("rating"), validators=[MinValueValidator(0), MaxValueValidator(5)], default=0
    )

    # Read: https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return "{}: {}".format(self.from_user, self.title)
