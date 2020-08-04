from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..models import Calendar, Event


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["name"]


class EventSerializer(serializers.ModelSerializer):
    calendar = CalendarSerializer(required=True)

    class Meta:
        model = Event
        fields = ["title", "start", "end", "calendar"]

