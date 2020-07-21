from django.urls import path
from . import views


urlpatterns = [
    path("meeting/end/<uuid:meeting_id>/", views.end_meeting_callback),
]
