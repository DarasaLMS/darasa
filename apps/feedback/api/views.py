from rest_framework import viewsets
from rest_framework import permissions
from ..models import Feedback
from .serializers import FeedbackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = [permissions.IsAuthenticated]
