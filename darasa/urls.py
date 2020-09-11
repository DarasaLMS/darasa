"""darasa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, re_path
from django.views.static import serve
from dotenv import load_dotenv
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import api_urls

load_dotenv(os.path.join(settings.BASE_DIR, ".env"))

SCHEMA_VIEW = get_schema_view(
    openapi.Info(
        title="{} API".format(os.getenv("SITE_NAME", "Darasa LMS")),
        default_version="v1",
        description="",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT License"),
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = os.getenv("SITE_NAME", "Darasa LMS")
admin.site.site_title = os.getenv("SITE_NAME", "Darasa LMS")
admin.site.site_url = "{}/admin".format(os.getenv("SITE_URL", "http://localhost:8000"))
admin.site.index_title = "Administration"

urlpatterns = [
    re_path(
        r"^docs/$", SCHEMA_VIEW.with_ui("swagger", cache_timeout=0), name="api-docs"
    ),
    re_path(r"^(?P<version>(v1))/", include(api_urls)),
    re_path("admin/", admin.site.urls),
    re_path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    re_path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    re_path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT, "show_indexes": True},
        )
    ]
