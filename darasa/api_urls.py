from django.conf import settings
from django.urls import include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    re_path(
        r"^accounts/",
        include(("apps.accounts.api.urls", "accounts-api"), namespace="accounts-api"),
    ),
]
