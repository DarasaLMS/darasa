from rest_framework import routers
from django.urls import include, re_path
from .views import (
    CourseViewSet,
    ClassroomView,
    ClassroomCreateView,
    end_meeting_callback,
    RequestView,
    UserClassroomsView,
    UserCoursesView,
)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(
        r"^classrooms/$",
        ClassroomCreateView.as_view(),
        name="api_classroom",
    ),
    re_path(
        r"^classrooms/(?P<classroom_id>.+)/$",
        ClassroomView.as_view(),
        name="api_classroom",
    ),
    re_path(r"^meetings/(?P<meeting_id>.+)/end/$", end_meeting_callback),
    re_path(
        r"^requests/(?P<request_id>.+)/$", RequestView.as_view(), name="api_request",
    ),
    re_path(
        r"^users/(?P<user_id>.+)/classrooms/$",
        UserClassroomsView.as_view(),
        name="api_user_classrooms",
    ),
    re_path(
        r"^users/(?P<user_id>.+)/courses/$",
        UserCoursesView.as_view(),
        name="api_user_courses",
    ),
]
