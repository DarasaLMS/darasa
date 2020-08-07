from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.classrooms.api.serializers import ClassroomSerializer
from ..models import Calendar, Event, Rule


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["id", "name"]


class RuleSerializer(serializers.ModelSerializer):
    rrule_frequency = serializers.ReadOnlyField()

    class Meta:
        model = Rule
        fields = [
            "id",
            "name",
            "description",
            "frequency",
            "params",
            "rrule_frequency",
        ]


class EventSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer()
    calendar = CalendarSerializer()
    rule = RuleSerializer(required=False)

    class Meta:
        model = Event
        fields = [
            "id",
            "start",
            "end",
            "classroom",
            "rule",
            "end_recurring_period",
            "calendar",
            "color_event",
        ]

