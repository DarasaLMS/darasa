from rest_framework import routers
from django.urls import include, re_path
from .views import (
    CourseViewSet,
    ClassroomCreateView,
    ClassroomView,
    create_join_meeting_room_link,
    end_meeting,
    check_running_meeting,
    RequestCreateView,
    RequestView,
    UserClassroomsView,
    UserCoursesView,
)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^classrooms/$", ClassroomCreateView.as_view(), name="api_classrooms",),
    re_path(
        r"^classrooms/(?P<classroom_id>.+)/$",
        ClassroomView.as_view(),
        name="api_classrooms",
    ),
    re_path(r"^rooms/(?P<room_id>.+)/join/$", create_join_meeting_room_link),
    re_path(r"^rooms/(?P<room_id>.+)/end/$", end_meeting),
    re_path(r"^rooms/(?P<room_id>.+)/running/$", check_running_meeting),
    re_path(r"^requests/$", RequestCreateView.as_view(), name="api_requests",),
    re_path(
        r"^requests/(?P<request_id>.+)/$", RequestView.as_view(), name="api_requests",
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
