import time
import uuid
import string
import random
from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from sorl.thumbnail import ImageField
from apps.core.models import BaseModel
from apps.core.tasks import send_email
from apps.core.bbb import (
    create_meeting,
    join_meeting_url,
    is_meeting_running,
    get_meeting_info,
    end_meeting,
)
from apps.accounts.models import Student, Teacher, EducationalStage
from .utils import get_random_password

REQUEST_ACCEPTED_TXT = get_template("emails/request_accepted.txt")
REQUEST_ACCEPTED_HTML = get_template("emails/request_accepted.html")

REQUEST_DECLINED_TXT = get_template("emails/request_declined.txt")
REQUEST_DECLINED_HTML = get_template("emails/request_declined.html")


class Course(BaseModel):
    JOIN_ALL = "join_all"
    CHOOSE_TO_JOIN = "choose_to_join"
    CLASSROOM_JOIN_MODES = (
        (JOIN_ALL, _("Join all clasrooms in this course")),
        (CHOOSE_TO_JOIN, _("Choose to join a classroom")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=256)
    description = models.TextField(_("description"), blank=True)
    cover = ImageField(
        upload_to="covers/%Y/%m",
        default="covers/default/cover.png",
        verbose_name=_("cover image"),
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="teacher",
        verbose_name=_("teacher"),
    )
    assistant_teachers = models.ManyToManyField(
        Teacher,
        related_name="assistant_teachers",
        verbose_name=_("assistant teachers"),
        blank=True,
        null=True,
    )
    students = models.ManyToManyField(Student, verbose_name=_("students"), blank=True)
    educational_stages = models.ManyToManyField(
        EducationalStage, verbose_name=_("educational stages"), blank=True
    )
    classroom_join_mode = models.CharField(
        _("classroom join mode"),
        max_length=32,
        choices=CLASSROOM_JOIN_MODES,
        default=JOIN_ALL,
    )

    def __str__(self):
        return "{}".format(self.name)

    @property
    def students_count(self):
        return self.students.count()

    def progress(self):
        # TODO: Implement course progress
        pass


class Lesson(BaseModel):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    notes = models.FileField(upload_to="notes/%Y/%m", null=True, blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        verbose_name=_("course"),
        related_name="lessons",
    )
    parent_lesson = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    position = models.IntegerField(_("position"), default=0)


class Post(BaseModel):
    FAQ = "faq"
    ANNOUNCEMENT = "announcement"
    POST_CATEGORIES = (
        (FAQ, _("Frequently Asked Questions (FAQ)")),
        (ANNOUNCEMENT, _("Announcements")),
    )

    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    category = models.CharField(
        _("category"), max_length=32, choices=POST_CATEGORIES, default=ANNOUNCEMENT,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        verbose_name=_("course"),
        related_name="posts",
    )
    parent_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )


class Classroom(BaseModel):
    def get_room_id():
        if Classroom.objects.all().count() == 0:
            return random.randrange(100000, 1000000000)
        else:
            return Classroom.objects.latest("date_created").room_id + 1

    # Class fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        verbose_name=_("course"),
        related_name="classrooms",
    )

    # Room fields
    room_id = models.IntegerField(
        _("room number"),
        help_text=_("The room number which need to be unique."),
        unique=True,
        default=get_room_id,
    )
    welcome_message = models.CharField(
        _("welcome message"),
        help_text=_("Message which displayed on the chat window."),
        max_length=200,
        blank=True,
    )
    logout_url = models.URLField(
        _("logout URL"),
        help_text=_("URL to which users will be redirected."),
        default=settings.BBB_LOGOUT_URL,
    )
    moderator_password = models.CharField(
        _("moderator password"), max_length=120, default=get_random_password
    )
    attendee_password = models.CharField(
        _("attendee password"), max_length=120, default=get_random_password
    )

    def __str__(self):
        return "{}".format(self.name)

    @property
    def start_date(self):
        """Returns a python datetime object"""
        return self.event.start

    @property
    def end_date(self):
        """Returns a python datetime object"""
        return self.event.end

    @property
    def duration(self):
        """Returns duration in seconds"""
        diff = self.end_date - self.start_date
        return diff.total_seconds()

    @property
    def recurring(self):
        return {
            "rule": self.event.rule,
            "end_recurring_period": self.event.end_recurring_period,
        }

    def create_meeting_room(self, duration=0):
        callback_url = "{}/{}/rooms/{}/end/".format(
            settings.SITE_URL, settings.API_VERSION, self.room_id
        )
        response = create_meeting(
            self.name,
            self.room_id,
            self.moderator_password,
            self.attendee_password,
            self.welcome_message,
            self.logout_url,
            callback_url,
            settings.BBB_URL,
            settings.BBB_SECRET,
            # Duration of the meeting in minutes.
            # Default is 0 (meeting doesn't end).
            duration,
        )

        if response.get("returncode") == "SUCCESS":
            return True

        return False

    def create_join_link(self, user, moderator=False):
        # create meeting room is idempotent.
        # Always a good idea to call each time to ensure meeting exists.
        self.create_meeting_room()

        is_teacher = user == self.course.teacher.user
        if is_teacher:
            moderator = True

        is_student = Course.objects.filter(id=self.course.id, students__user__in=[user])

        if is_teacher or is_student:
            url = join_meeting_url(
                self.room_id,
                str(user),
                str(user.id),
                self.moderator_password if moderator else self.attendee_password,
                settings.BBB_URL,
                settings.BBB_SECRET,
            )
            return url

        return None

    def is_meeting_running(self):
        response = is_meeting_running(
            self.room_id, settings.BBB_URL, settings.BBB_SECRET,
        )
        if response.get("returncode") == "SUCCESS":
            return response.get("running") == "true"

        return False

    def get_meeting_info(self):
        response = get_meeting_info(
            self.room_id,
            self.moderator_password,
            settings.BBB_URL,
            settings.BBB_SECRET,
        )
        return response

    def end_meeting(self, close_session=True):
        response = end_meeting(
            self.room_id,
            self.moderator_password,
            settings.BBB_URL,
            settings.BBB_SECRET,
        )
        if response.get("returncode") == "SUCCESS":
            return True

        return False


class StudentAttendance(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name=_("student")
    )
    occurrence = models.ForeignKey(
        "timetable.Occurrence", on_delete=models.CASCADE, verbose_name=_("occurrence")
    )
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

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=True, blank=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classrooms = models.ManyToManyField(
        Classroom, blank=True, help_text=_("Preferred classrooms to join")
    )
    status = models.CharField(max_length=16, choices=STATUS, default=PENDING)

    _status = None

    class Meta:
        unique_together = [["student", "course"]]

    def __str__(self):
        return "{} requested to enroll in {}".format(self.student, self.course)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = self.status

    def process_student_request(self):
        classrooms = []
        if self.course.classroom_join_mode == Course.JOIN_ALL:
            classrooms = self.course.classrooms.all()
        elif self.course.classroom_join_mode == Course.CHOOSE_TO_JOIN:
            classrooms = self.classrooms.all()

        if self.status == Request.ACCEPTED:
            # Add student to course
            self.course.students.add(self.student)
            # Add classroom to student's calendar
            for classroom in classrooms:
                if classroom.event:
                    classroom.event.calendars.add(self.student.user.calendar)

            self.send_student_accept_email(classrooms)

        elif self.status == Request.DECLINED:
            self.send_student_decline_email()

    def send_student_accept_email(self, classrooms):
        data = {
            "first_name": self.student.user.first_name,
            "course": self.course,
            "classrooms": classrooms,
            "site_name": settings.SITE_NAME,
        }
        text_content = REQUEST_ACCEPTED_TXT.render(data)
        html_content = REQUEST_ACCEPTED_HTML.render(data)
        send_email.delay(
            "Request to enroll in course {} has been accepted".format(self.course.name),
            text_content,
            self.student.user.email,
            html_content=html_content,
        )

    def send_student_decline_email(self):
        data = {
            "first_name": self.student.user.first_name,
            "course": self.course.name,
            "site_name": settings.SITE_NAME,
        }
        text_content = REQUEST_DECLINED_TXT.render(data)
        html_content = REQUEST_DECLINED_HTML.render(data)
        send_email.delay(
            "Request to enroll in course {} has been declined".format(self.course.name),
            text_content,
            self.student.user.email,
            html_content=html_content,
        )


@receiver(post_save, sender=Request)
def post_save_request(sender, instance, created, **kwargs):
    if created:
        instance.teacher = instance.course.teacher
        instance.save()

    if instance._status == Request.PENDING and instance.status == Request.ACCEPTED:
        instance.process_student_request()

