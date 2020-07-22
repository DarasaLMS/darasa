from rest_framework import routers
from django.urls import include, re_path, path
from .views import (
    ClassroomViewSet,
    CourseViewSet,
    TopicViewSet,
    RequestViewSet,
    end_meeting_callback,
)

router = routers.DefaultRouter()
router.register(r"", ClassroomViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"topics", TopicViewSet)
router.register(r"requests", RequestViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    path("end-meeting/<uuid:meeting_id>/", end_meeting_callback),
]
