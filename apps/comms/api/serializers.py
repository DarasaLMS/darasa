from rest_framework import serializers
from apps.accounts.api.serializers import UserSerializer
from ..models import Message


class MessageSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(many=False, read_only=True)
    to_user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "from_user",
            "to_user",
            "title",
            "description",
            "category",
            "rating",
            "content_object",
            "date_modified",
        ]
