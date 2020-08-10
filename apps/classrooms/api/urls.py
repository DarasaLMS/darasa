from rest_framework import routers
from django.urls import include, re_path
from .views import (
    CourseViewSet,
    ClassroomView,
    end_meeting_callback,
    RequestView,
)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^(?P<classroom_id>.+)/$", ClassroomView.as_view(), name="api_classroom",),
    re_path(r"^meeting/(?P<meeting_id>.+)/end/$", end_meeting_callback),
    re_path(r"^requests/(?P<request_id>.+)/$", RequestView.as_view(), name="api_request",),
]
