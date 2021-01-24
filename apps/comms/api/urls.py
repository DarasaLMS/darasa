from rest_framework import routers
from django.urls import include, re_path, path
from .views import MessageViewSet

router = routers.DefaultRouter()
router.register(r"messages", MessageViewSet)

urlpatterns = [re_path(r"^", include(router.urls))]
