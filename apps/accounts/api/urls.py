from django.urls import re_path
from .views import (
    LoginView,
    UserListAPIView,
    create_user_view,
    UserRetrieveAPIView,
    verify_account,
    reset_password,
    request_password_reset,
    EducationalStageCreateAPIView,
    EducationalStageListAPIView,
    EducationalStageRetrieveUpdateDestroyAPIView,
    SchoolCreateAPIView,
    SchoolListAPIView,
    SchoolRetrieveUpdateAPIView,
)

urlpatterns = [
    re_path(r"^login/$", LoginView.as_view(), name="login_obtain_token"),
    re_path(r"^users/create/$", create_user_view, name="create_user_view"),
    re_path(r"^users/$", UserListAPIView.as_view(), name="users_list_view"),
    re_path(
        r"^users/(?P<user_id>.+)/$",
        UserRetrieveAPIView.as_view(),
        name="user_retrieve_view",
    ),
    re_path(r"^verification/$", verify_account, name="verify_account"),
    re_path(r"^password-reset/$", reset_password, name="reset_password"),
    re_path(
        r"^password-reset/request/$",
        request_password_reset,
        name="request_password_reset",
    ),
    re_path(
        r"^educational-stages/create/$",
        EducationalStageCreateAPIView.as_view(),
        name="educational_stages_create_view",
    ),
    re_path(
        r"^educational-stages/$",
        EducationalStageListAPIView.as_view(),
        name="educational_stages_list_view",
    ),
    re_path(
        r"^educational-stages/(?P<stage_id>.+)/$$",
        EducationalStageRetrieveUpdateDestroyAPIView.as_view(),
        name="educational_stages_view",
    ),
    re_path(
        r"^schools/create$", SchoolCreateAPIView.as_view(), name="school_create_view"
    ),
    re_path(r"^schools/$", SchoolListAPIView.as_view(), name="schools_list_view"),
    re_path(
        r"^schools/(?P<school_id>.+)/$$",
        SchoolRetrieveUpdateAPIView.as_view(),
        name="schools_view",
    ),
]
