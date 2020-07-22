from rest_framework import serializers
from apps.feedback.models import Feedback
from apps.accounts.api.serializers import UserSerializer
from apps.classrooms.api.serializers import ClassroomSerializer


class FeedbackSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(many=False, read_only=True)
    to_user = UserSerializer(many=False, read_only=True)
    classroom = ClassroomSerializer(many=False, read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "id",
            "from_user",
            "to_user",
            "message",
            "classroom",
            "rating",
            "date_modified",
        ]

