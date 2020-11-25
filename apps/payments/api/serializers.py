from rest_framework import serializers
from apps.accounts.api.serializers import MiniUserSerializer
from apps.schools.api.serializers import ClassroomSerializer, CourseSerializer
from ..models import Billing, Payment, Rate


class BillingSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(many=False, read_only=True)

    class Meta:
        model = Billing
        fields = [
            "id",
            "user",
            "address_1",
            "address_2",
            "city",
            "state",
            "postal_code",
            "country",
            "active",
            "date_modified",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    billing = BillingSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "course",
            "billing",
            "customer_ip_address",
            "transaction_reference",
            "total_amount",
            "captured_amount",
            "charge_status",
            "date_modified",
        ]


class RateSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)

    class Meta:
        model = Rate
        fields = ["course", "price", "date_modified"]
