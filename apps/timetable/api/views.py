import datetime
import pytz
from django.conf import settings
from django.db.models import F, Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView
from rest_framework import exceptions, permissions, status
from ..models import Calendar, Event, Occurrence
from ..periods import weekday_names
from ..settings import (
    CHECK_EVENT_PERM_FUNC,
    CHECK_OCCURRENCE_PERM_FUNC,
    EVENT_NAME_PLACEHOLDER,
)
from ..utils import check_calendar_permissions
from .serializers import CalendarSerializer


class CalendarView(ListAPIView):
    serializer_class = CalendarSerializer
    queryset = Calendar.objects.all()
    permission_classes = [permissions.IsAuthenticated]


@check_calendar_permissions
def api_occurrences(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    calendar_slug = request.GET.get("calendar_slug")
    timezone = request.GET.get("timezone")

    try:
        response_data = _api_occurrences(start, end, calendar_slug, timezone)
    except (ValueError, Calendar.DoesNotExist) as e:
        return HttpResponseBadRequest(e)

    return JsonResponse(response_data, safe=False)


def _api_occurrences(start, end, calendar_slug, timezone):

    if not start or not end:
        raise ValueError("Start and end parameters are required")
    # version 2 of full calendar
    # TODO: improve this code with date util package
    if "-" in start:

        def convert(ddatetime):
            if ddatetime:
                ddatetime = ddatetime.split(" ")[0]
                try:
                    return datetime.datetime.strptime(ddatetime, "%Y-%m-%d")
                except ValueError:
                    # try a different date string format first before failing
                    return datetime.datetime.strptime(ddatetime, "%Y-%m-%dT%H:%M:%S")

    else:

        def convert(ddatetime):
            return datetime.datetime.utcfromtimestamp(float(ddatetime))

    start = convert(start)
    end = convert(end)
    current_tz = False
    if timezone and timezone in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(timezone)
        start = current_tz.localize(start)
        end = current_tz.localize(end)
    elif settings.USE_TZ:
        # If USE_TZ is True, make start and end dates aware in UTC timezone
        utc = pytz.UTC
        start = utc.localize(start)
        end = utc.localize(end)

    if calendar_slug:
        # will raise DoesNotExist exception if no match
        calendars = [Calendar.objects.get(slug=calendar_slug)]
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
    # for more info https://github.com/llazzaro/django-scheduler/pull/169
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
                    "title": occurrence.title,
                    "start": event_start,
                    "end": event_end,
                    "existed": existed,
                    "event_id": occurrence.event.id,
                    "color": occurrence.event.color_event,
                    "description": occurrence.description,
                    "rule": recur_rule,
                    "end_recurring_period": recur_period_end,
                    "creator": str(occurrence.event.creator),
                    "calendar": occurrence.event.calendar.slug,
                    "cancelled": occurrence.cancelled,
                }
            )
    return response_data


@require_POST
@check_calendar_permissions
def api_move_or_resize_by_code(request):
    response_data = {}
    user = request.user
    id = request.POST.get("id")
    existed = bool(request.POST.get("existed") == "true")
    delta = datetime.timedelta(minutes=int(request.POST.get("delta")))
    resize = bool(request.POST.get("resize", False))
    event_id = request.POST.get("event_id")

    response_data = _api_move_or_resize_by_code(
        user, id, existed, delta, resize, event_id
    )

    return JsonResponse(response_data)


def _api_move_or_resize_by_code(user, id, existed, delta, resize, event_id):
    response_data = {}
    response_data["status"] = "PERMISSION DENIED"

    if existed:
        occurrence = Occurrence.objects.get(id=id)
        occurrence.end += delta
        if not resize:
            occurrence.start += delta
        if CHECK_OCCURRENCE_PERM_FUNC(occurrence, user):
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
        if CHECK_EVENT_PERM_FUNC(event, user):
            event.save()
            event.occurrence_set.all().update(
                original_start=F("original_start") + dts,
                original_end=F("original_end") + dte,
            )
            response_data["status"] = "OK"
    return response_data


@require_POST
@check_calendar_permissions
def api_select_create(request):
    response_data = {}
    start = request.POST.get("start")
    end = request.POST.get("end")
    calendar_slug = request.POST.get("calendar_slug")

    response_data = _api_select_create(start, end, calendar_slug)

    return JsonResponse(response_data)


def _api_select_create(start, end, calendar_slug):
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)

    calendar = Calendar.objects.get(slug=calendar_slug)
    Event.objects.create(
        start=start, end=end, title=EVENT_NAME_PLACEHOLDER, calendar=calendar
    )

    response_data = {}
    response_data["status"] = "OK"
    return response_data
