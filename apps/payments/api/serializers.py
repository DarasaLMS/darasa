from rest_framework import serializers
from apps.payments.models import Billing, Payment, Rate
from apps.accounts.api.serializers import UserSerializer
from apps.classrooms.api.serializers import (
    ClassroomSerializer,
    CourseSerializer,
    TopicSerializer,
)


class BillingSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

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
    classroom = ClassroomSerializer(many=False, read_only=True)
    billing = BillingSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "classroom",
            "billing",
            "customer_ip_address",
            "transaction_reference",
            "total_amount",
            "captured_amount",
            "charge_status",
            "date_modified",
        ]


class RateSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(many=False, read_only=True)
    course = CourseSerializer(many=False, read_only=True)
    topic = TopicSerializer(many=False, read_only=True)

    class Meta:
        model = Rate
        fields = [
            "id",
            "classroom",
            "course",
            "topic",
            "price",
            "date_modified",
        ]
