from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from .models import Classroom
from .api.serializers import ClassroomSerializer


@api_view(["POST", "GET"])
def end_meeting_callback(request, meeting_id):
    classroom = get_object_or_404(Classroom.objects.all(), meeting_id=meeting_id)
    classroom.end_meeting()
    return Response(ClassroomSerializer(instance=classroom).data)
