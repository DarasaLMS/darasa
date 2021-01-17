from django.urls import re_path
from .views import (
    LoginView,
    UserListAPIView,
    create_user_view,
    UserRetrieveUpdateAPIView,
    verify_account,
    reset_password,
    request_password_reset,
)

urlpatterns = [
    re_path(r"^login/$", LoginView.as_view(), name="login_obtain_token"),
    re_path(r"^users/create/$", create_user_view, name="create_user_view"),
    re_path(r"^users/$", UserListAPIView.as_view(), name="users_list_view"),
    re_path(
        r"^users/(?P<user_id>.+)/$",
        UserRetrieveUpdateAPIView.as_view(),
        name="user_retrieve_update_view",
    ),
    re_path(r"^verification/$", verify_account, name="verify_account"),
    re_path(r"^password-reset/$", reset_password, name="reset_password"),
    re_path(
        r"^password-reset/request/$",
        request_password_reset,
        name="request_password_reset",
    ),
]
