import datetime
import dateutil.parser
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
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.validators import is_valid_uuid
from apps.accounts.models import User
from apps.timetable.models import Event, Rule
from ..models import (
    School,
    Level,
    Student,
    Teacher,
    Course,
    Lesson,
    Post,
    Classroom,
    Request,
)
from .serializers import (
    SchoolSerializer,
    LevelSerializer,
    CourseSerializer,
    ClassroomSerializer,
    RequestSerializer,
    LessonSerializer,
    PostSerializer,
)


class SchoolListAPIView(generics.ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.AllowAny]


class SchoolCreateAPIView(generics.CreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]


class SchoolRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "school_id"


class LevelListAPIView(generics.ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.AllowAny]


class LevelCreateAPIView(generics.CreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]


class LevelRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "level_id"


class CoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["levels"]

    def get_queryset(self):
        queryset = Course.objects.all().order_by("date_modified")
        recommended = self.request.query_params.get("recommended", None)
        if recommended == "true":
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


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "description": openapi.Schema(type=openapi.TYPE_STRING),
            "levels": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
            ),
            "classroom_join_mode": openapi.Schema(type=openapi.TYPE_STRING),
            "cover": openapi.Schema(type=openapi.TYPE_STRING),
            "teacher": openapi.Schema(type=openapi.TYPE_STRING),
            "assistant_teachers": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
            ),
        },
    ),
)
@api_view(["POST"])
def create_course_view(request, *args, **kwargs):
    name = request.data.get("name", None)
    description = request.data.get("description", None)
    levels = request.data.get("levels", "")
    classroom_join_mode = request.data.get("classroom_join_mode", None)
    cover = request.data.get("cover", None)
    teacher_user_id = request.data.get("teacher", None)
    assistant_teachers = request.data.get("assistant_teachers", "")

    try:
        teacher = get_object_or_404(Teacher.objects.all(), user__id=teacher_user_id)
        course, course_created = Course.objects.get_or_create(
            name=name, teacher=teacher
        )

        if course_created:
            course.created_by = request.user
        else:
            course.modified_by = request.user

        course.description = description
        course.classroom_join_mode = classroom_join_mode
        course.cover = cover
        course.save()

        for level_id in levels.split(","):
            if not level_id:
                continue

            level = get_object_or_404(Level.objects.all(), id=level_id)
            if level not in course.levels.all():
                course.levels.add(level)

        for ateacher_user_id in assistant_teachers.split(","):
            if not ateacher_user_id:
                continue

            assistant_teacher = get_object_or_404(
                Teacher.objects.all(), user__id=ateacher_user_id
            )
            if assistant_teacher not in course.assistant_teachers.all():
                course.assistant_teachers.add(assistant_teacher)

        return Response(CourseSerializer(instance=course).data)

    except Exception as error:
        raise exceptions.APIException(error)


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


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "description": openapi.Schema(type=openapi.TYPE_STRING),
            "notes": openapi.Schema(type=openapi.TYPE_STRING),
            "parent_lesson": openapi.Schema(type=openapi.TYPE_STRING),
            "position": openapi.Schema(type=openapi.TYPE_STRING),
            "course_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
def create_lesson_view(request, *args, **kwargs):
    name = request.data.get("name", None)
    description = request.data.get("description", None)
    notes = request.data.get("notes", None)
    parent_lesson = request.data.get("parent_lesson", None)
    position = request.data.get("position", 0)
    course_id = request.data.get("course_id", None)

    try:
        course = get_object_or_404(Course.objects.all(), id=course_id)
        lesson, lesson_created = Lesson.objects.get_or_create(name=name, course=course)

        if lesson_created:
            lesson.created_by = request.user
        else:
            lesson.modified_by = request.user

        lesson.description = description
        lesson.notes = notes
        lesson.parent_lesson = Lesson.objects.filter(id=parent_lesson).first()
        lesson.position = position
        lesson.save()

        return Response(LessonSerializer(instance=lesson).data)

    except Exception as error:
        raise exceptions.APIException(error)


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "description": openapi.Schema(type=openapi.TYPE_STRING),
            "parent_post": openapi.Schema(type=openapi.TYPE_STRING),
            "category": openapi.Schema(type=openapi.TYPE_STRING),
            "course_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
def create_post_view(request, *args, **kwargs):
    name = request.data.get("name", None)
    description = request.data.get("description", None)
    parent_post = request.data.get("parent_post", None)
    category = request.data.get("category", None)
    course_id = request.data.get("course_id", None)

    try:
        course = get_object_or_404(Course.objects.all(), id=course_id)
        post, post_created = Post.objects.get_or_create(name=name, course=course)

        if post_created:
            post.created_by = request.user
        else:
            post.modified_by = request.user

        post.description = description
        post.parent_post = Post.objects.filter(id=parent_post).first()
        post.category = category
        post.save()

        return Response(PostSerializer(instance=post).data)

    except Exception as error:
        raise exceptions.APIException(error)


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "description": openapi.Schema(type=openapi.TYPE_STRING),
            "welcome_message": openapi.Schema(type=openapi.TYPE_STRING),
            "duration": openapi.Schema(type=openapi.TYPE_NUMBER),
            "start_datetime": openapi.Schema(type=openapi.TYPE_STRING),
            "repeat": openapi.Schema(type=openapi.TYPE_STRING),
            "repeat_until": openapi.Schema(type=openapi.TYPE_STRING),
            "color": openapi.Schema(type=openapi.TYPE_STRING),
            "course_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
def create_classroom_view(request, *args, **kwargs):
    name = request.data.get("name", None)
    description = request.data.get("description", None)
    welcome_message = request.data.get("welcome_message", None)
    duration = request.data.get("duration", 0)
    start_datetime = request.data.get("start_datetime", None)
    repeat = request.data.get("repeat", "")
    repeat_until = request.data.get("repeat_until", None)
    color = request.data.get("color", None)
    course_id = request.data.get("course_id", None)

    try:
        course = get_object_or_404(Course.objects.all(), id=course_id)
        classroom, classroom_created = Classroom.objects.get_or_create(
            name=name, course=course
        )

        if classroom_created:
            classroom.created_by = request.user
        else:
            classroom.modified_by = request.user

        classroom.description = description
        classroom.welcome_message = welcome_message
        classroom.save()

        rule, _ = Rule.objects.get_or_create(name=repeat.lower(), frequency=repeat)

        # Parse dates
        start = dateutil.parser.parse(start_datetime)
        end = start + datetime.timedelta(minutes=int(duration))
        end_recurring_period = dateutil.parser.parse(repeat_until)

        event, event_created = Event.objects.get_or_create(
            start=start, end=end, classroom=classroom
        )

        if event_created:
            event.created_by = request.user
        else:
            event.modified_by = request.user

        event.rule = rule
        event.end_recurring_period = end_recurring_period
        event.color = color
        event.save()
        # Add scheduled class to teachers calendar
        event.calendars.add(course.teacher.user.calendar)

        return Response(ClassroomSerializer(instance=classroom).data)

    except Exception as error:
        raise exceptions.APIException(error)


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
    search_fields = [
        "course__name",
        "status",
        "student__user__first_name",
        "student__user__last_name",
    ]
    filterset_fields = ["status", "course__name"]

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
