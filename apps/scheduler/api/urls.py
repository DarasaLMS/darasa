from django.conf.urls import url
from django.views.generic.list import ListView
from ..models import Calendar
from .views import (
    api_move_or_resize_by_code,
    api_occurrences,
    api_select_create,
)

urlpatterns = [
    url(r"^occurrences", api_occurrences, name="api_occurrences"),
    url(r"^move_or_resize/$", api_move_or_resize_by_code, name="api_move_or_resize"),
    url(r"^select_create/$", api_select_create, name="api_select_create"),
    url(r"^$", ListView.as_view(queryset=Calendar.objects.all()), name="schedule"),
]
