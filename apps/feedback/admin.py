from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    list_display = (
        "message",
        "rating",
        "course",
        "from_user",
        "to_user",
        "date_modified",
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
