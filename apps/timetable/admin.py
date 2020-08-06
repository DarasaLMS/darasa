from django.contrib import admin
from .forms import EventAdminForm
from .models import (
    Calendar,
    CalendarRelation,
    Event,
    EventRelation,
    Occurrence,
    Rule,
)


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    fieldsets = ((None, {"fields": [("name",)]}),)


@admin.register(CalendarRelation)
class CalendarRelationAdmin(admin.ModelAdmin):
    list_display = ("calendar", "content_object")
    list_filter = ("inheritable",)
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "calendar",
                    ("content_type", "object_id", "distinction"),
                    "inheritable",
                ]
            },
        ),
    )


@admin.register(EventRelation)
class EventRelationAdmin(admin.ModelAdmin):
    list_display = ("event", "content_object", "distinction")
    fieldsets = (
        (None, {"fields": ["event", ("content_type", "object_id", "distinction")]}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end")
    list_filter = ("start",)
    ordering = ("-start",)
    date_hierarchy = "start"
    search_fields = ("title", "description")
    fieldsets = (
        (
            None,
            {
                "fields": [
                    ("title", "color_event"),
                    ("description",),
                    ("start", "end"),
                    ("creator", "calendar"),
                    ("rule", "end_recurring_period"),
                ]
            },
        ),
    )
    form = EventAdminForm


admin.site.register(Occurrence, admin.ModelAdmin)


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "frequency")
    list_filter = ("frequency",)
    search_fields = ("name", "description")
