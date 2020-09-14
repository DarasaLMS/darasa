from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    exceptions,
    permissions,
    status,
    viewsets,
    generics,
    mixins,
    filters,
)
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.accounts.models import Student
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.validators import is_valid_uuid
from apps.accounts.models import User
from ..models import Course, Classroom, Request
from .serializers import CourseSerializer, ClassroomSerializer, RequestSerializer


class ListCreateCourseView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["educational_stages"]

    def get_queryset(self):
        queryset = Course.objects.all().order_by("date_modified")
        proposed = self.request.query_params.get("proposed", None)
        if proposed == "true":
            if self.request.user.role == "student":
                return queryset.exclude(students__user__in=[self.request.user])
            elif self.request.user.role == "teacher":
                return queryset.exclude(
                    Q(teacher__user=self.request.user)
                    | Q(assistant_teachers__user__in=[self.request.user])
                ).distinct()

        return queryset

    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CourseView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Course.objects.all().order_by("date_modified")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "course_id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter("course_id", openapi.IN_PATH, type=openapi.TYPE_STRING)
    ],
)
@api_view(["GET"])
def has_requested_course(request, course_id, *args, **kwargs):
    course = get_object_or_404(Course.objects.all(), id=course_id)
    return Response({"status": course.has_requested_course(request.user)})


@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter("course_id", openapi.IN_PATH, type=openapi.TYPE_STRING)
    ],
)
@api_view(["GET"])
def has_joined_course(request, course_id, *args, **kwargs):
    course = get_object_or_404(Course.objects.all(), id=course_id)
    return Response({"status": course.has_joined_course(request.user)})


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
        openapi.Parameter("room_id", openapi.IN_PATH, type=openapi.TYPE_STRING)
    ],
)
@api_view(["PATCH"])
def end_meeting(request, room_id, *args, **kwargs):
    classroom = get_object_or_404(Classroom.objects.all(), room_id=room_id)
    classroom.end_meeting()
    return Response(ClassroomSerializer(instance=classroom).data)


@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        openapi.Parameter("room_id", openapi.IN_PATH, type=openapi.TYPE_STRING)
    ],
)
@api_view(["POST"])
def create_join_meeting_room_link(request, room_id, *args, **kwargs):
    classroom = get_object_or_404(Classroom.objects.all(), room_id=room_id)
    meeting_room_link = classroom.create_join_link(request.user)
    return Response({"meeting_room_link": meeting_room_link})


@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter("room_id", openapi.IN_PATH, type=openapi.TYPE_STRING)
    ],
)
@api_view(["GET"])
def check_running_meeting(request, room_id, *args, **kwargs):
    classroom = get_object_or_404(Classroom.objects.all(), room_id=room_id)
    return Response({"status": classroom.is_meeting_running()})


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "course_id": openapi.Schema(type=openapi.TYPE_STRING),
            "user_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
def create_request_view(request, *args, **kwargs):
    course_id = request.data.get("course_id", None)
    user_id = request.data.get("user_id", None)
    course = get_object_or_404(Course.objects.all(), id=course_id)
    user = get_object_or_404(User.objects.all(), id=user_id)
    try:
        request, _ = Request.objects.get_or_create(course=course, student=user.student)
        return Response(RequestSerializer(instance=request).data)
    except Exception as error:
        raise exceptions.APIException(error)


class RequestView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView
):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "request_id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        request_id = kwargs.get("request_id", None)
        new_status = request.data.get("status", None)
        course_request = get_object_or_404(Request.objects.all(), id=request_id)
        course_request.process_student_request(new_status)
        return self.update(request, *args, **kwargs)


class UserClassroomsView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if not is_valid_uuid(user_id):
            raise exceptions.ValidationError("Invalid user_id")

        if user_id:
            try:
                user = User.objects.filter(id=user_id).first()
                self.queryset = self.queryset.filter(
                    Q(course__teacher__user=user)
                    | Q(course__assistant_teachers__user__in=[user])
                    | Q(course__students__user__in=[user])
                )
                if user.role == "teacher":
                    self.queryset = self.queryset.distinct()

            except Exception as error:
                raise exceptions.APIException(error)

        return super().get(self, request, *args, **kwargs)


class UserCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if not is_valid_uuid(user_id):
            raise exceptions.ValidationError("Invalid user_id")

        if user_id:
            try:
                user = User.objects.filter(id=user_id).first()
                self.queryset = self.queryset.filter(
                    Q(teacher__user=user)
                    | Q(assistant_teachers__user__in=[user])
                    | Q(students__user__in=[user])
                )
                if user.role == "teacher":
                    self.queryset = self.queryset.distinct()

            except Exception as error:
                raise exceptions.APIException(error)

        return super().get(self, request, *args, **kwargs)


class UserRequestsView(generics.ListAPIView):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["course__name"]
    filterset_fields = ["status"]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if not is_valid_uuid(user_id):
            raise exceptions.ValidationError("Invalid user_id")

        if user_id:
            try:
                self.queryset = self.queryset.filter(
                    Q(teacher__user__id=user_id) | Q(student__user__id=user_id)
                )
            except Exception as error:
                raise exceptions.APIException(error)

        return super().get(self, request, *args, **kwargs)
