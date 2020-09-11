from rest_framework import routers
from django.urls import include, re_path, path
from .views import PaymentViewSet, BillingViewSet, RateViewSet

router = routers.DefaultRouter()
router.register(r"", PaymentViewSet)
router.register(r"billings", BillingViewSet)
router.register(r"rates", RateViewSet)

urlpatterns = [re_path(r"^", include(router.urls))]
