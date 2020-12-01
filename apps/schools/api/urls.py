from django.urls import include, re_path
from .views import (
    SchoolCreateAPIView,
    SchoolListAPIView,
    SchoolRetrieveUpdateAPIView,
    LevelCreateAPIView,
    LevelListAPIView,
    LevelRetrieveUpdateDestroyAPIView,
    CoursesView,
    create_course_view,
    CourseView,
    has_requested_course,
    has_joined_course,
    create_lesson_view,
    create_post_view,
    create_classroom_view,
    ClassroomView,
    create_join_meeting_room_link,
    end_meeting,
    check_running_meeting,
    create_request_view,
    RequestView,
    UserClassroomsView,
    UserCoursesView,
    UserRequestsView,
)

urlpatterns = [
    re_path(
        r"^schools/create$", SchoolCreateAPIView.as_view(), name="school_create_view"
    ),
    re_path(r"^schools/$", SchoolListAPIView.as_view(), name="schools_list_view"),
    re_path(
        r"^schools/(?P<school_id>.+)/$$",
        SchoolRetrieveUpdateAPIView.as_view(),
        name="schools_view",
    ),
    re_path(
        r"^levels/create/$", LevelCreateAPIView.as_view(), name="levels_create_view"
    ),
    re_path(r"^levels/$", LevelListAPIView.as_view(), name="levels_list_view"),
    re_path(
        r"^levels/(?P<level_id>.+)/$$",
        LevelRetrieveUpdateDestroyAPIView.as_view(),
        name="levels_view",
    ),
    re_path(r"^courses/$", CoursesView.as_view()),
    re_path(r"^courses/add/$", create_course_view),
    re_path(r"^courses/(?P<course_id>.+)/requested/$", has_requested_course),
    re_path(r"^courses/(?P<course_id>.+)/joined/$", has_joined_course),
    re_path(r"^courses/(?P<course_id>.+)/$", CourseView.as_view()),
    re_path(r"^lessons/$", create_lesson_view),
    re_path(r"^posts/$", create_post_view),
    re_path(r"^classrooms/$", create_classroom_view),
    re_path(r"^classrooms/(?P<classroom_id>.+)/$", ClassroomView.as_view()),
    re_path(r"^rooms/(?P<room_id>.+)/join/$", create_join_meeting_room_link),
    re_path(r"^rooms/(?P<room_id>.+)/end/$", end_meeting),
    re_path(r"^rooms/(?P<room_id>.+)/running/$", check_running_meeting),
    re_path(r"^requests/$", create_request_view),
    re_path(r"^requests/(?P<request_id>.+)/$", RequestView.as_view()),
    re_path(r"^users/(?P<user_id>.+)/classrooms/$", UserClassroomsView.as_view()),
    re_path(r"^users/(?P<user_id>.+)/courses/$", UserCoursesView.as_view()),
    re_path(r"^users/(?P<user_id>.+)/requests/$", UserRequestsView.as_view()),
]
