import datetime
import pytz
import dateutil.parser
from django.conf import settings
from django.db.models import F, Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, permissions, status, viewsets, generics, mixins
from apps.core.permissions import IsOwnerOrReadOnly
from apps.schools.api.serializers import StudentPictureSerializer
from apps.schools.models import Classroom
from ..models import Calendar, Event, Occurrence, Rule
from .serializers import EventSerializer, RuleSerializer


class EventDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_url_kwarg = "event_id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RuleViewset(viewsets.ModelViewSet):
    serializer_class = RuleSerializer
    queryset = Rule.objects.all()
    permission_classes = [permissions.IsAuthenticated]


@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter("calendar_id", openapi.IN_PATH, type=openapi.TYPE_STRING),
        openapi.Parameter("start", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        openapi.Parameter("end", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        openapi.Parameter("timezone", openapi.IN_QUERY, type=openapi.TYPE_STRING),
    ],
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def api_occurrences(request, calendar_id, **kwargs):
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    tz = request.query_params.get("timezone")
    include_students = request.query_params.get("include_students") == "true"

    try:
        response_data = _api_occurrences(
            request, start, end, calendar_id, tz, include_students
        )
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Calendar.DoesNotExist as e:
        return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(response_data)


# flake8: noqa: C901
def _api_occurrences(request, start, end, calendar_id, tz, include_students=False):
    if not start or not end:
        raise ValueError("Start and end datetime parameters are required")

    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)

    current_tz = False
    if tz and tz in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(tz)
        start = current_tz.localize(start)
        end = current_tz.localize(end)
    elif settings.USE_TZ:
        # If USE_TZ is True, make start and end dates aware in UTC timezone
        utc = pytz.UTC
        start = utc.localize(start)
        end = utc.localize(end)

    if calendar_id:
        # will raise DoesNotExist exception if no match
        calendars = [Calendar.objects.get(id=calendar_id)]
    # if no calendar slug is given, get all the calendars
    else:
        calendars = Calendar.objects.all()

    response_data = []
    # Algorithm to get an id for the occurrences in fullcalendar (NOT THE SAME
    # AS IN THE DB) which are always unique.
    # Fullcalendar thinks that all their "events" with the same "event.id" in
    # their system are the same object, because it's not really built around
    # the idea of events (generators)
    # and occurrences (their events).
    # Check the "persisted" boolean value that tells it whether to change the
    # event, using the "event_id" or the occurrence with the specified "id".
    i = 1
    if Occurrence.objects.all().count() > 0:
        i = Occurrence.objects.latest("id").id + 1
    event_list = []
    for calendar in calendars:
        # create flat list of events from each calendar
        event_list += calendar.events.filter(start__lte=end).filter(
            Q(end_recurring_period__gte=start) | Q(end_recurring_period__isnull=True)
        )
    for event in event_list:
        occurrences = event.get_occurrences(start, end)
        for occurrence in occurrences:
            occurrence_id = i + occurrence.event.id
            existed = False

            if occurrence.id:
                occurrence_id = occurrence.id
                existed = True

            recur_rule = occurrence.event.rule.name if occurrence.event.rule else None

            if occurrence.event.end_recurring_period:
                recur_period_end = occurrence.event.end_recurring_period
                if current_tz:
                    # make recur_period_end aware in given timezone
                    recur_period_end = recur_period_end.astimezone(current_tz)
                recur_period_end = recur_period_end
            else:
                recur_period_end = None

            event_start = occurrence.start
            event_end = occurrence.end
            if current_tz:
                # make event start and end dates aware in given timezone
                event_start = event_start.astimezone(current_tz)
                event_end = event_end.astimezone(current_tz)

            response_data.append(
                {
                    "id": occurrence_id,
                    "title": occurrence.name,
                    "description": occurrence.description,
                    "start": event_start,
                    "end": event_end,
                    "existed": existed,
                    "event_id": occurrence.event.id,
                    "classroom": {
                        "name": occurrence.event.classroom.name,
                        "duration": occurrence.event.classroom.duration,
                        "room_id": occurrence.event.classroom.room_id,
                    },
                    "course": {
                        "name": occurrence.event.classroom.course.name,
                        "teacher": str(occurrence.event.classroom.course.teacher),
                        "students": StudentPictureSerializer(
                            occurrence.event.classroom.course.students.all(),
                            many=True,
                            context={"request": request},
                        ).data
                        if include_students
                        else [],
                    },
                    "color": occurrence.event.color,
                    "rule": recur_rule,
                    "end_recurring_period": recur_period_end,
                    "created_by": str(occurrence.event.created_by),
                    "cancelled": occurrence.cancelled,
                }
            )

    return response_data


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "existed": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "delta": openapi.Schema(
                type=openapi.TYPE_NUMBER, description="delta in minutes"
            ),
            "resize": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "event_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsOwnerOrReadOnly])
def api_move_or_resize_by_code(request, occurrence_id, **kwargs):
    response_data = {}
    user = request.user
    existed = bool(request.data.get("existed") == "true")
    delta = datetime.timedelta(minutes=int(request.data.get("delta")))
    resize = bool(request.data.get("resize", False))
    event_id = request.data.get("event_id")

    try:
        response_data = _api_move_or_resize_by_code(
            user, occurrence_id, existed, delta, resize, event_id
        )
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(response_data)


def _api_move_or_resize_by_code(user, occurrence_id, existed, delta, resize, event_id):
    response_data = {}

    if existed:
        occurrence = Occurrence.objects.get(id=occurrence_id)
        occurrence.end += delta
        if not resize:
            occurrence.start += delta
        occurrence.save()
        response_data["status"] = "OK"
    else:
        event = Event.objects.get(id=event_id)
        dts = 0
        dte = delta
        if not resize:
            event.start += delta
            dts = delta
        event.end = event.end + delta
        event.save()
        event.occurrence_set.all().update(
            original_start=F("original_start") + dts,
            original_end=F("original_end") + dte,
        )
        response_data["status"] = "OK"

    return response_data


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "start": openapi.Schema(type=openapi.TYPE_STRING),
            "end": openapi.Schema(type=openapi.TYPE_STRING),
            "classroom_id": openapi.Schema(type=openapi.TYPE_STRING),
            "calendar_id": openapi.Schema(type=openapi.TYPE_STRING),
            "rule_id": openapi.Schema(type=openapi.TYPE_STRING),
            "end_recurring_period": openapi.Schema(type=openapi.TYPE_STRING),
            "color": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["start", "end", "classroom_id", "calendar_id"],
    ),
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsOwnerOrReadOnly])
def api_create_event(request, **kwargs):
    start = request.data.get("start")
    end = request.data.get("end")
    classroom_id = request.data.get("classroom_id")
    calendar_id = request.data.get("calendar_id")
    rule_id = request.data.get("rule_id", None)
    end_recurring_period = request.data.get("end_recurring_period", None)
    color = request.data.get("color", None)

    try:
        if not start or not end:
            raise ValueError("Start and end parameters are required")

        start = dateutil.parser.parse(start)
        end = dateutil.parser.parse(end)

        classroom = Classroom.objects.get(id=classroom_id)
        calendar = Calendar.objects.get(id=calendar_id)

        rule = None
        if rule_id:
            rule = Rule.objects.filter(id=rule_id).first()

        event = Event.objects.create(
            start=start,
            end=end,
            classroom=classroom,
            rule=rule,
            end_recurring_period=end_recurring_period,
            color=color,
        )
        event.calendars.add(calendar)

        return Response(EventSerializer(instance=event).data)

    except (ValueError, Classroom.DoesNotExist, Calendar.DoesNotExist) as e:
        return Response(
            {"message": str(e), "class": e.__class__.__name__},
            status=status.HTTP_400_BAD_REQUEST,
        )
