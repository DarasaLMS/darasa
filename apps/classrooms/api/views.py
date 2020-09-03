from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import exceptions, permissions, status, viewsets, generics, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from apps.accounts.models import Student
from apps.core.permissions import IsOwnerOrReadOnly
from ..models import Course, Classroom, Request
from .serializers import (
    CourseSerializer,
    ClassroomSerializer,
    RequestSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


class ClassroomCreateView(generics.CreateAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClassroomView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = "classroom_id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@swagger_auto_schema(
    method="PATCH",
    manual_parameters=[
        openapi.Parameter("meeting_id", openapi.IN_PATH, type=openapi.TYPE_STRING,),
    ],
)
@api_view(["PATCH"])
def end_meeting_callback(request, meeting_id):
    classroom = get_object_or_404(Classroom.objects.all(), meeting_id=meeting_id)
    classroom.end_meeting()
    return Response(ClassroomSerializer(instance=classroom).data)


class RequestView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = "request_id"

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserClassroomsView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if user_id:
            student = Student.objects.filter(user__id=user_id).first()
            self.queryset = self.queryset.filter(
                Q(course__teacher__user__id=user_id)
                | Q(course__assistant_teacher__user__id=user_id)
                | Q(course__students__in=[student])
            )
        return super().get(self, request, *args, **kwargs)


class UserCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if user_id:
            student = Student.objects.filter(user__id=user_id).first()
            self.queryset = self.queryset.filter(
                Q(teacher__user__id=user_id)
                | Q(assistant_teacher__user__id=user_id)
                | Q(students__in=[student])
            )
        return super().get(self, request, *args, **kwargs)
