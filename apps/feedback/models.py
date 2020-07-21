import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.classrooms.models import Classroom
from apps.core.models import BaseModel


class Feedback(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="from_user_feedback"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="to_user_feedback"
    )
    message = models.TextField(blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = [["from_user", "to_user", "classroom"]]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return "{} {}".format(self.from_user, self.rating)
