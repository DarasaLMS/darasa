from django.urls import re_path, path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    LoginView,
    UserListView,
    create_user_view,
    UserRetrieveView,
    verify_account,
    reset_password,
    request_password_reset,
    EducationalStageViewset,
    SchoolViewset,
)

router = routers.DefaultRouter()
router.register(r"educational-stages", EducationalStageViewset)
router.register(r"schools", SchoolViewset)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^login/$", LoginView.as_view(), name="login_obtain_token"),
    re_path(r"^users/$", UserListView.as_view(), name="users_list_view"),
    re_path(r"^users/signup/$", create_user_view, name="create_user_view"),
    re_path(
        r"^users/(?P<user_id>.+)/$",
        UserRetrieveView.as_view(),
        name="user_retrieve_view",
    ),
    re_path(r"^verification/$", verify_account, name="verify_account"),
    re_path(r"^password-reset/$", reset_password, name="reset_password"),
    re_path(
        r"^password-reset/request/$",
        request_password_reset,
        name="request_password_reset",
    ),
]
