from django.conf import settings
from django.urls import include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    re_path(
        r"^", include(("apps.schools.api.urls", "schools-api"), namespace="schools-api")
    ),
    re_path(
        r"^accounts/",
        include(("apps.accounts.api.urls", "accounts-api"), namespace="accounts-api"),
    ),
    re_path(
        r"^comms/", include(("apps.comms.api.urls", "comms-api"), namespace="comms-api")
    ),
    re_path(
        r"^payments/",
        include(("apps.payments.api.urls", "payments-api"), namespace="payments-api"),
    ),
    re_path(
        r"^timetable/",
        include(
            ("apps.timetable.api.urls", "timetable-api"), namespace="timetable-api"
        ),
    ),
]
