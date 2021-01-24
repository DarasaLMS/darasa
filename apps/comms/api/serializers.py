from rest_framework import serializers
from ..models import Message


class MessageSerializer(serializers.ModelSerializer):
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
