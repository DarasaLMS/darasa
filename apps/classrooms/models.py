import time
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from apps.core.models import BaseModel
from apps.core.bbb import (
    get_meeting_info,
    create_meeting,
    end_meeting,
    join_meeting_url,
)
from apps.accounts.models import User, Student, Teacher
from apps.core.tasks import send_email

CLASSROOM_MODERATOR_TXT = get_template("emails/classroom_moderator.txt")
CLASSROOM_MODERATOR_HTML = get_template("emails/classroom_moderator.txt")

REQUEST_APPROVED_TXT = get_template("emails/request_approved.txt")
REQUEST_APPROVED_HTML = get_template("emails/request_approved.html")

REQUEST_REJECTED_TXT = get_template("emails/request_rejected.txt")
REQUEST_REJECTED_HTML = get_template("emails/request_rejected.html")


class Course(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return "{}".format(self.title)


class Classroom(BaseModel):
    REPEAT_CHOICES = (
        ("never", _("Doesn't repeat")),
        ("daily", _("Daily")),
        ("weekly", _("Weekly")),
        ("monthly", _("Monthly")),
        ("annually", _("Annually")),
        ("weekday", _("Every Weekday (Mon - Fri)")),
        ("weekend", _("Every Weekend (Sat - Sun)")),
    )

    def get_meeting_id():
        if Classroom.objects.all().count() == 0:
            return randrange(100000, 1000000)
        else:
            return Classroom.objects.latest("created_at").meeting_id + 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        _("Name"), help_text=_("The name of the classroom."), max_length=256
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )
    students = models.ManyToManyField(Student)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    meeting_id = models.IntegerField(
        _("Meeting ID"),
        help_text=_("The meeting number which need to be unique."),
        unique=True,
        default=get_meeting_id,
    )
    welcome_message = models.CharField(
        _("Welcome message"),
        help_text=_("Message which displayed on the chat window."),
        max_length=200,
        blank=True,
    )
    logout_url = models.URLField(
        _("Logout URL"),
        help_text=_("URL to which users will be redirected."),
        default=settings.BBB_LOGOUT_URL,
    )

    moderator_password = models.CharField(max_length=120, null=True)
    attendee_password = models.CharField(max_length=120, null=True)

    repeats = models.CharField(max_length=32, choices=REPEAT_CHOICES, default="never")
    class_time = models.TimeField(_("Class time"))
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    # Duration of the meeting in minutes. Default is 0 (meeting doesn't end).
    duration = models.PositiveIntegerField(default=0)

    started_class = models.BooleanField(default=False)
    starting_class = models.BooleanField(default=False)
    started_class_at = models.DateTimeField(null=True, blank=True)

    finished_class = models.BooleanField(default=False)
    finished_class_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    def create_meeting_room(self):
        if not self.starting_class:
            self.starting_class = True
            callback_url = "{}/classrooms/end-meeting/{}".format(
                settings.API_HOST, self.meeting_id
            )
            response = create_meeting(
                self.name,
                self.meeting_id,
                self.moderator_password,
                self.attendee_password,
                self.welcome_message,
                self.logout_url,
                callback_url,
                settings.BBB_URL,
                settings.BBB_SECRET,
                self.duration,
            )

            if response.get("returncode") == "SUCCESS":
                self.moderator_password = response.get("moderatorPW")
                self.attendee_password = response.get("attendeePW")
                self.started_class_at = timezone.now()
                self.started_class = True
                self.starting_class = False

            self.save()
        else:
            while self.starting_class:
                time.sleep(0.05)
                self.refresh_from_db(fields=["starting_class"])

    def create_join_link(self, user, moderator=False):
        if not self.started_class:
            self.create_meeting_room()

        is_teacher = user == self.teacher
        if is_teacher:
            moderator = True

        is_student = user in self.students.all()

        if (is_teacher or is_student) and self.started_class:
            response = join_meeting_url(
                self.meeting_id,
                str(self.user),
                str(user.id),
                self.moderator_password if moderator else self.attendee_password,
                settings.BBB_URL,
                settings.BBB_SECRET,
            )
            # Send email with join link
            return response.get("url")

        return None

    def get_meeting_info(self):
        response = get_meeting_info(
            self.meeting_id,
            self.moderator_password,
            settings.BBB_URL,
            settings.BBB_SECRET,
        )
        return response

    def end_meeting(self, close_session=True):
        response = end_meeting(
            self.meeting_id,
            self.moderator_password,
            settings.BBB_URL,
            settings.BBB_SECRET,
        )
        if response.get("returncode") == "SUCCESS":
            self.finished_class = True
            self.finished_class_at = timezone.now()
            self.save()

    def estimate_duration(self):
        if self.duration:
            return self.duration

        if self.started_class_at:
            if self.finished_class_at:
                return self.finished_class_at - self.started_class_at
            else:
                return timezone.now() - self.started_class_at
        else:
            return 0


@receiver(post_save, sender=Classroom)
def _create_meeting_room(sender, instance, created, **kwargs):
    if created:
        instance.create_meeting_room()
        meeting_url = instance.classroom.create_join_link(instance.teacher)
        data = {
            "first_name": instance.teacher.user.first_name,
            "classroom": instance.classroom,
            "meeting_url": meeting_url,
            "site_name": settings.SITE_NAME,
        }
        text_content = CLASSROOM_MODERATOR_TXT.render(data)
        html_content = CLASSROOM_MODERATOR_HTML.render(data)
        send_email.delay(
            "Join Classroom {}".format(instance.classroom),
            text_content,
            instance.student.user.email,
            html_content=html_content,
        )


class Request(BaseModel):
    STATUS = (
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("pending", "Pending"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=True, blank=True
    )
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")

    _status = None

    class Meta:
        unique_together = [["student", "classroom"]]

    def __str__(self):
        return "{} requested class {}".format(self.student, self.classroom)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = self.status


@receiver(post_save, sender=Request)
def _process_request(sender, instance, created, **kwargs):
    if instance._status != instance.status:
        if instance.status == "approved":
            instance.classroom.students.add(instance.student)
            meeting_url = instance.classroom.create_join_link(instance.student)
            data = {
                "first_name": instance.student.user.first_name,
                "classroom": instance.classroom,
                "meeting_url": meeting_url,
                "site_name": settings.SITE_NAME,
            }
            text_content = REQUEST_APPROVED_TXT.render(data)
            html_content = REQUEST_APPROVED_HTML.render(data)
            send_email.delay(
                "Join Classroom {}".format(instance.classroom),
                text_content,
                instance.student.user.email,
                html_content=html_content,
            )

        if instance.status == "rejected":
            data = {
                "first_name": instance.student.user.first_name,
                "classroom": instance.classroom,
                "site_name": settings.SITE_NAME,
            }
            text_content = REQUEST_REJECTED_TXT.render(data)
            html_content = REQUEST_REJECTED_HTML.render(data)
            send_email.delay(
                "Request for Classroom {}".format(instance.classroom),
                text_content,
                instance.student.user.email,
                html_content=html_content,
            )
