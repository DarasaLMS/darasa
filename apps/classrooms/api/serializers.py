from django.conf import settings
from rest_framework import serializers
from apps.classrooms.models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = [
            "name",
            "meeting_id",
        ]

