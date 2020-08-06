from django.urls import re_path
from django.urls import path, include
from django.views.generic.list import ListView
from ..models import Calendar
from .views import (
    EventDetailView,
    api_occurrences,
    api_select_create,
    api_move_or_resize_by_code,
)

urlpatterns = [
    re_path(
        r"^events/(?P<event_id>.+)/$",
        EventDetailView.as_view(),
        name="api_events",
    ),
    re_path(
        r"^calendars/(?P<calendar_id>.+)/occurrences/$",
        api_occurrences,
        name="api_occurrences",
    ),
    re_path(
        r"^calendars/(?P<calendar_id>.+)/events/$",
        api_select_create,
        name="api_select_create",
    ),
    re_path(
        r"^occurrences/(?P<occurrence_id>.+)/change/$",
        api_move_or_resize_by_code,
        name="api_move_or_resize",
    ),
]
