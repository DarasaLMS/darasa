from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = (
        "from_user",
        "to_user",
        "title",
        "description",
        "rating",
        "date_modified",
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
