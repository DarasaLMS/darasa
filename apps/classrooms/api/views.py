from django.db.models import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from apps.classrooms.models import Course, Classroom, Request
from .serializers import (
    CourseSerializer,
    ClassroomSerializer,
    RequestSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = []

    def get_queryset(self):
        return self.queryset.filter(
            Q(students__in=self.request.user) | Q(teacher=self.request.user)
        )


@api_view(["POST", "GET"])
def end_meeting_callback(request, meeting_id):
    classroom = get_object_or_404(Classroom.objects.all(), meeting_id=meeting_id)
    classroom.end_meeting()
    return Response(ClassroomSerializer(instance=classroom).data)


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    permission_classes = [permissions.IsAuthenticated]
