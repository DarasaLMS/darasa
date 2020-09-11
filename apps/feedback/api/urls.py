from rest_framework import routers
from django.urls import include, re_path, path
from .views import FeedbackViewSet

router = routers.DefaultRouter()
router.register(r"feedback", FeedbackViewSet)

urlpatterns = [re_path(r"^", include(router.urls))]
