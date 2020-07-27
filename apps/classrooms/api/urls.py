from rest_framework import routers
from django.urls import include, re_path
from .views import (
    ClassroomViewSet,
    CourseViewSet,
    RequestViewSet,
    end_meeting_callback,
)

router = routers.DefaultRouter()
router.register(r"", ClassroomViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"requests", RequestViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^m/(?P<meeting_id>.+)/end/$", end_meeting_callback),
]
