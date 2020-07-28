import time
import uuid
from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django.template.defaultfilters import slugify
from sorl.thumbnail import ImageField
from apps.scheduler.models import Event, Occurrence
from apps.core.models import BaseModel
from apps.core.tasks import send_email
from apps.core.bbb import (
    get_meeting_info,
    create_meeting,
    end_meeting,
    join_meeting_url,
)
from apps.accounts.models import User, Student, Teacher

CLASSROOM_MODERATOR_TXT = get_template("emails/classroom_moderator.txt")
CLASSROOM_MODERATOR_HTML = get_template("emails/classroom_moderator.txt")

REQUEST_ACCEPTED_TXT = get_template("emails/request_accepted.txt")
REQUEST_ACCEPTED_HTML = get_template("emails/request_accepted.html")

REQUEST_DECLINED_TXT = get_template("emails/request_declined.txt")
REQUEST_DECLINED_HTML = get_template("emails/request_declined.html")


class Course(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    cover = ImageField(
        upload_to="covers/%Y/%m", default="covers/default/cover.png"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="teacher"
    )
    assistant_teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="assistant_teacher"
    )
    students = models.ManyToManyField(Student)

    def __str__(self):
        return "{}".format(self.title)


class Classroom(BaseModel):
    def get_meeting_id():
        if Classroom.objects.all().count() == 0:
            return randrange(100000, 1000000)
        else:
            return Classroom.objects.latest("created_at").meeting_id + 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=200, unique=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)

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
    # Duration of the meeting in minutes. Default is 0 (meeting doesn't end).
    duration = models.PositiveIntegerField(default=0)

    groups = models.ManyToManyField(
        Course, through="ClassroomGroup", related_name="course_classroom_groups"
    )

    def __str__(self):
        return "{}".format(self.name)

    @property
    def ongoing(self):
        return True

    def create_meeting_room(self):
        callback_url = "{}/classrooms/m/{}/end/".format(
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
            self.save()
            return True

        self.save()
        return False

    def create_join_link(self, user, moderator=False):
        if not self.meeting_id:
            self.create_meeting_room()

        is_teacher = user == self.course.teacher
        if is_teacher:
            moderator = True

        is_student = user in self.students.all()

        if is_teacher or is_student:
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
            self.ongoing = False
            self.save()
            info_response = self.get_meeting_info()
            if info_response.get("returncode") == "SUCCESS":
                print(info_response)


@receiver(pre_save, sender=Classroom)
def pre_save_user(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)


@receiver(post_save, sender=Classroom)
def _create_meeting_room(sender, instance, created, **kwargs):
    if created:
        if instance.create_meeting_room():
            meeting_url = instance.create_join_link(instance.course.teacher)
            data = {
                "first_name": instance.course.teacher.user.first_name,
                "classroom": instance.name,
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


class ClassroomGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return "{}".format(self.name)


@receiver(pre_save, sender=ClassroomGroup)
def pre_save_user(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)


class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}: {} - {}".format(self.student, self.joined_at, self.left_at)


class Request(BaseModel):
    ACCEPTED = "accepted"
    DECLINED = "declined"
    PENDING = "pending"
    STATUS = (
        (ACCEPTED, _("Accepted")),
        (DECLINED, _("Declined")),
        (PENDING, _("Pending")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=True, blank=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS, default=PENDING)

    _status = None

    class Meta:
        unique_together = [["student", "course"]]

    def __str__(self):
        return "{} requested to enroll in {}".format(self.student, self.course)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = self.status


@receiver(post_save, sender=Request)
def _process_request(sender, instance, created, **kwargs):
    if instance._status != instance.status:
        if instance.status == Request.ACCEPTED:
            instance.course.students.add(instance.student)
            meeting_url = instance.classroom.create_join_link(instance.student)
            data = {
                "first_name": instance.student.user.first_name,
                "classroom": instance.classroom.name,
                "meeting_url": meeting_url,
                "site_name": settings.SITE_NAME,
            }
            text_content = REQUEST_ACCEPTED_TXT.render(data)
            html_content = REQUEST_ACCEPTED_HTML.render(data)
            send_email.delay(
                "Join Classroom {}".format(instance.classroom.name),
                text_content,
                instance.student.user.email,
                html_content=html_content,
            )

        if instance.status == Request.DECLINED:
            data = {
                "first_name": instance.student.user.first_name,
                "classroom": instance.classroom.name,
                "site_name": settings.SITE_NAME,
            }
            text_content = REQUEST_DECLINED_TXT.render(data)
            html_content = REQUEST_DECLINED_HTML.render(data)
            send_email.delay(
                "Request declined for Classroom {}".format(instance.classroom).name,
                text_content,
                instance.student.user.email,
                html_content=html_content,
            )
