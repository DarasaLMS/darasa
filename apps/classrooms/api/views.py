from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import exceptions, permissions, status, viewsets, generics, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from ..models import Course, Classroom, Request
from .serializers import (
    CourseSerializer,
    ClassroomSerializer,
    RequestSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]


class ClassroomView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = "classroom_id"

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

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
