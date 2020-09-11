from rest_framework import viewsets
from rest_framework import permissions
from .serializers import BillingSerializer, PaymentSerializer, RateSerializer
from ..models import Billing, Payment, Rate


class BillingViewSet(viewsets.ModelViewSet):
    serializer_class = BillingSerializer
    queryset = Billing.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class RateViewSet(viewsets.ModelViewSet):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
