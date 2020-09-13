from django.urls import include, re_path
from .views import (
    ListCreateCourseView,
    CourseView,
    has_requested_course,
    has_joined_course,
    ClassroomCreateView,
    ClassroomView,
    create_join_meeting_room_link,
    end_meeting,
    check_running_meeting,
    create_request_view,
    RequestView,
    UserClassroomsView,
    UserCoursesView,
)

urlpatterns = [
    re_path(r"^courses/$", ListCreateCourseView.as_view()),
    re_path(r"^courses/(?P<course_id>.+)/requested/$", has_requested_course),
    re_path(r"^courses/(?P<course_id>.+)/joined/$", has_joined_course),
    re_path(r"^courses/(?P<course_id>.+)/$", CourseView.as_view()),
    re_path(r"^classrooms/$", ClassroomCreateView.as_view(), name="api_classrooms"),
    re_path(
        r"^classrooms/(?P<classroom_id>.+)/$",
        ClassroomView.as_view(),
        name="api_classrooms",
    ),
    re_path(r"^rooms/(?P<room_id>.+)/join/$", create_join_meeting_room_link),
    re_path(r"^rooms/(?P<room_id>.+)/end/$", end_meeting),
    re_path(r"^rooms/(?P<room_id>.+)/running/$", check_running_meeting),
    re_path(r"^requests/$", create_request_view),
    re_path(
        r"^requests/(?P<request_id>.+)/$", RequestView.as_view(), name="api_requests"
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
