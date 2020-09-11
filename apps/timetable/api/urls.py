from django.urls import re_path
from django.urls import path, include
from django.views.generic.list import ListView
from rest_framework import routers
from ..models import Calendar
from .views import (
    EventDetailView,
    RuleViewset,
    api_occurrences,
    api_create_event,
    api_move_or_resize_by_code,
)

router = routers.DefaultRouter()
router.register(r"rules", RuleViewset)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^events/$", api_create_event, name="api_create_event"),
    re_path(
        r"^events/(?P<event_id>.+)/$", EventDetailView.as_view(), name="api_events"
    ),
    re_path(
        r"^calendars/(?P<calendar_id>.+)/occurrences/$",
        api_occurrences,
        name="api_calendar_occurrences",
    ),
    re_path(
        r"^occurrences/(?P<occurrence_id>.+)/change/$",
        api_move_or_resize_by_code,
        name="api_calendar_move_or_resize_occurrences",
    ),
]
