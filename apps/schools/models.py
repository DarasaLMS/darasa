import time
import uuid
import string
import random
import logging
from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from sorl.thumbnail import ImageField
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import BaseModel
from apps.core.tasks import send_email
from apps.core.bbb import (
    create_meeting,
    join_meeting_url,
    is_meeting_running,
    get_meeting_info,
    end_meeting,
)
from apps.accounts.models import User
from .utils import get_random_password

logger = logging.getLogger(__name__)

REQUEST_ACCEPTED_TXT = get_template("emails/request_accepted.txt")
REQUEST_ACCEPTED_HTML = get_template("emails/request_accepted.html")

REQUEST_DECLINED_TXT = get_template("emails/request_declined.txt")
REQUEST_DECLINED_HTML = get_template("emails/request_declined.html")

REQUEST_SUSPENDED_TXT = get_template("emails/request_suspended.txt")
REQUEST_SUSPENDED_HTML = get_template("emails/request_suspended.html")

TEACHER_VERIFICATION_TXT = get_template("emails/teacher_verification.txt")
TEACHER_VERIFICATION_HTML = get_template("emails/teacher_verification.html")


class School(models.Model):
    """
    This is a singleton model that can only hold one record of a School at a time.
    """

    ENROLL_ALL = "enroll_all"
    CHOOSE_TO_ENROLL = "choose_to_enroll"
    COURSE_ENROLL_MODES = (
        (ENROLL_ALL, _("Enroll to all courses per student's level")),
        (CHOOSE_TO_ENROLL, _("Choose to enroll to a course")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    moto = models.CharField(max_length=256, blank=True)
    logo = ImageField(upload_to="logos/%Y/%m", default="logos/default/logo.png")
    phone = PhoneNumberField(_("phone number"), blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    support_email = models.EmailField(_("support email address"), blank=True, null=True)
    about = RichTextField(blank=True)
    terms_and_privacy = RichTextField(blank=True)
    footer_text = models.CharField(max_length=256, blank=True)
    enroll_mode = models.CharField(
        _("course enroll mode"),
        max_length=32,
        choices=COURSE_ENROLL_MODES,
        default=ENROLL_ALL,
    )
    allow_teacher_verification = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.name)


@receiver(pre_save, sender=School)
def pre_save_school(sender, instance, **kwargs):
    if School.objects.exclude(pk=instance.pk).exists():
        raise ValidationError("You can only have one school")


class Level(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)

    def __str__(self):
        return "{}".format(self.name)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    @property
    def active_classes(self):
        return self.classroom_set.all()

    @property
    def pending_requests(self):
        return self.request_set.all().filter(status="pending")

    @property
    def approved_requests(self):
        return self.request_set.all().filter(status="approved")

    @property
    def rejected_requests(self):
        return self.request_set.all().filter(status="rejected")


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="teacher"
    )
    position = models.CharField(max_length=256, blank=True)
    bio = models.TextField(blank=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    verified = models.BooleanField(default=False)
    verification_file = models.FileField(
        upload_to="verifications/%Y/%m", null=True, blank=True
    )

    _was_verified = None

    def __str__(self):
        return "{} {} {}".format(
            str(self.user.title or "").title(),
            str(self.user.first_name or "").title(),
            str(self.user.last_name or "").title(),
        )

    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)
        self._was_verified = self.verified

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self._was_verified != self.verified:
            self.send_verified_email()

        return super(Teacher, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    @property
    def courses(self):
        return self.course_set.all()

    @property
    def classrooms(self):
        return self.classroom_set.all()

    @property
    def duration(self):
        raise NotImplementedError

    def feedback(self):
        raise NotImplementedError

    def rating(self):
        raise NotImplementedError

    def availability(self, datetime):
        return not self.classrooms.filter(
            start_class_at__gte=datetime, finish_class_at__lte=datetime
        ).exists()

    def send_verified_email(self):
        subject = "Verification for {}".format(settings.SITE_NAME)
        to_email = self.user.email
        data = {
            "first_name": self.user.first_name,
            "login_url": settings.HOST,
            "site_name": settings.SITE_NAME,
        }
        text_content = TEACHER_VERIFICATION_TXT.render(data)
        html_content = TEACHER_VERIFICATION_HTML.render(data)
        send_email.delay(subject, text_content, to_email, html_content=html_content)


@receiver(pre_save, sender=Teacher)
def delete_document_if_verified(sender, instance, **kwargs):
    if instance.verified and instance.verification_file:
        try:
            instance.verification_file.delete(save=False)
            instance.verification_file = None
        except Exception:
            logger.exception("Exception occured while trying to delete verified file")


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
    )
    students = models.ManyToManyField(Student, verbose_name=_("students"), blank=True)
    levels = models.ManyToManyField(Level, verbose_name=_("levels"), blank=True)
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

    def has_requested_course(self, user):
        return self.requests.filter(student__user=user).exists()

    def has_joined_course(self, user):
        return self.students.filter(user=user).exists()

    def progress(self):
        # TODO: Implement course progress
        pass


class Lesson(BaseModel):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    notes = models.FileField(upload_to="notes/%Y/%m", null=True, blank=True)
    position = models.IntegerField(_("position"), default=0)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        verbose_name=_("course"),
        related_name="lessons",
    )
    parent_lesson = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children_lessons",
    )


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
        _("category"), max_length=32, choices=POST_CATEGORIES, default=ANNOUNCEMENT
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, verbose_name=_("course"), related_name="posts"
    )
    parent_post = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children_posts",
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
    description = models.TextField(_("description"), null=True, blank=True)
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
            self.room_id, settings.BBB_URL, settings.BBB_SECRET
        )
        if response.get("returncode") == "SUCCESS":
            return response.get("running") == "true"

        return False

    def get_meeting_info(self):
        response = get_meeting_info(
            self.room_id, self.moderator_password, settings.BBB_URL, settings.BBB_SECRET
        )
        return response

    def end_meeting(self, close_session=True):
        response = end_meeting(
            self.room_id, self.moderator_password, settings.BBB_URL, settings.BBB_SECRET
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
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="requests"
    )
    classrooms = models.ManyToManyField(
        Classroom, blank=True, help_text=_("preferred classrooms to join")
    )
    status = models.CharField(max_length=16, choices=STATUS, default=PENDING)

    class Meta:
        unique_together = [["student", "course"]]

    def __str__(self):
        return "{} requested to enroll in {}".format(self.student, self.course)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_student_request(self, status):
        classrooms = []
        if self.course.classroom_join_mode == Course.JOIN_ALL:
            classrooms = self.course.classrooms.all()
        elif self.course.classroom_join_mode == Course.CHOOSE_TO_JOIN:
            classrooms = self.classrooms.all()

        if status == Request.ACCEPTED:
            if self.student not in self.course.students.all():
                # Add student to course
                self.course.students.add(self.student)
                # Add classroom to student's calendar
                for classroom in classrooms:
                    if classroom.event and (
                        self.student.user.calendar
                        not in classroom.event.calendars.all()
                    ):
                        classroom.event.calendars.add(self.student.user.calendar)

                self.send_student_accept_email(classrooms)

        elif status == Request.PENDING or status == Request.DECLINED:
            # Remove student if already added to course
            if self.student in self.course.students.all():
                self.course.students.remove(self.student)
                for classroom in classrooms:
                    classroom.event.calendars.remove(self.student.user.calendar)

            if status == Request.PENDING:
                self.send_student_suspend_email()

            if status == Request.DECLINED:
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

    def send_student_suspend_email(self):
        data = {
            "first_name": self.student.user.first_name,
            "course": self.course.name,
            "teacher": self.teacher,
            "site_name": settings.SITE_NAME,
        }
        text_content = REQUEST_SUSPENDED_TXT.render(data)
        html_content = REQUEST_SUSPENDED_HTML.render(data)
        send_email.delay(
            "You have been suspended from {} course".format(self.course.name),
            text_content,
            self.student.user.email,
            html_content=html_content,
        )


@receiver(post_save, sender=Request)
def post_save_request(sender, instance, created, **kwargs):
    if created:
        instance.teacher = instance.course.teacher
        instance.save()
