import uuid
import logging
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.core import validators
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import get_template
from sorl.thumbnail import ImageField
from django.utils.translation import ugettext_lazy as _
from apps.core.tasks import send_email

logger = logging.getLogger(__name__)

EMAIL_VERIFICATION_TXT = get_template("emails/email_verification.txt")
EMAIL_VERIFICATION_HTML = get_template("emails/email_verification.html")

PASSWORD_RESET_TXT = get_template("emails/password_reset.txt")
PASSWORD_RESET_HTML = get_template("emails/password_reset.html")

TEACHER_VERIFICATION_TXT = get_template("emails/teacher_verification.txt")
TEACHER_VERIFICATION_HTML = get_template("emails/teacher_verification.html")


class UserManager(BaseUserManager):
    """
    Manages creation of user accounts
    """

    def _create_user(self, email, password, **extra_fields):
        """ Creates user given email and password """
        if not email:
            raise ValueError("Users must have a valid email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Creates standard user account without any privileges"""
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Creates user account with superuser privileges """
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class VerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)


class PasswordResetToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model represents a person interacting with the system
    """

    USER_TYPE = (
        (0, "Staff"),
        (1, "Student"),
        (2, "Teacher"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("First name"), max_length=24, blank=True)
    last_name = models.CharField(_("Last name"), max_length=24, blank=True)
    nickname = models.CharField(_("Nickname"), max_length=24, blank=True)
    gender = models.CharField(
        _("Gender"),
        max_length=6,
        blank=True,
        choices=(("M", _("Male")), ("F", _("Female"))),
    )
    email = models.EmailField(_("Email address"), unique=True)
    email_verified = models.BooleanField(_("Email verified"), default=False)
    phone = models.CharField(_("Phone number"), max_length=16, unique=True)
    picture = ImageField(
        upload_to="pictures/%Y/%m", default="pictures/default/user.png"
    )
    user_type = models.IntegerField(_("User type"), choices=USER_TYPE, default=1)
    accepted_terms = models.BooleanField(
        _("Accepted terms and conditions"), default=False
    )
    is_staff = models.BooleanField(_("Staff"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    date_joined = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
    ]
    objects = UserManager()

    __email = None

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__email = self.email

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.__email.lower() != self.email.lower():
            self.email_verified = False
            self.send_verification_email()

        return super(User, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def send_verification_email(self):
        if not self.email_verified:
            token = VerificationToken.objects.get_or_create(user=self)[0]
            subject, from_email, to_email = (
                "Welcome to {}".format(settings.SITE_NAME),
                settings.DEFAULT_FROM_EMAIL,
                self.email,
            )
            data = {
                "first_name": self.first_name,
                "verification_url": "{}/account/verify?token={}".format(
                    settings.HOST, str(token.token)
                ),
                "site_name": settings.SITE_NAME,
            }
            text_content = EMAIL_VERIFICATION_TXT.render(data)
            html_content = EMAIL_VERIFICATION_HTML.render(data)
            send_email(
                subject, text_content, to_email, html_content=html_content
            ).delay()

    def check_email_verification(self, check_token):
        if str(self.verificationtoken.token) == str(check_token):
            self.email_verified = True
            self.verificationtoken.delete()
            self.save()
            return True
        else:
            return False

    def send_reset_mail(self):
        PasswordResetToken.objects.filter(user=self).delete()
        token = PasswordResetToken(user=self)
        token.save()
        subject, from_email, to_email = (
            "Reset password",
            settings.DEFAULT_FROM_EMAIL,
            self.email,
        )
        data = {
            "first_name": self.first_name,
            "email": self.email,
            "reset_url": "{}/account/password-reset/{}".format(
                settings.HOST, token.token
            ),
            "site_name": settings.SITE_NAME,
        }
        text_content = PASSWORD_RESET_TXT.render(data)
        html_content = PASSWORD_RESET_HTML.render(data)
        send_email(subject, text_content, to_email, html_content=html_content).delay()

    def billing_details(self):
        return self.billing_set.all().first()

    def payments(self):
        return self.billing_details().payments()


@receiver(post_save, sender=User)
def send_verify_on_creation(sender, instance, created, **kwargs):
    if created:
        instance.send_verification_email()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def active_classes(self):
        return self.classroom_set.all()

    def pending_requests(self):
        return self.request_set.all().filter(status="pending")

    def approved_requests(self):
        return self.request_set.all().filter(status="approved")

    def rejected_requests(self):
        return self.request_set.all().filter(status="rejected")


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    verified = models.BooleanField(default=False)
    verification_file = models.FileField(
        upload_to="verifications/%Y/%m", null=True, blank=True,
    )

    __was_verified = None

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)
        self.__was_verified = self.verified

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.__was_verified != self.verified:
            self.send_verified_email()

        return super(Teacher, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def courses(self):
        return self.course_set.all()

    def classrooms(self):
        return self.classroom_set.all()

    def duration(self):
        total_duration = 0
        for classroom in self.classrooms():
            total_duration += classroom.estimate_duration()

        return total_duration

    def feedback(self):
        return self.feedback_set.all()

    def rating(self):
        return self.feedback.aggregate(Avg("rating"))

    def availability(self, datetime):
        return not self.classrooms.filter(
            start_class_at__gte=datetime, finish_class_at__lte=datetime
        ).exists()

    def send_verified_email(self):
        subject, from_email, to_email = (
            "Verification for {}".format(settings.SITE_NAME),
            settings.DEFAULT_FROM_EMAIL,
            self.user.email,
        )
        data = {
            "first_name": self.user.first_name,
            "login_url": settings.HOST,
            "site_name": settings.SITE_NAME,
        }
        text_content = TEACHER_VERIFICATION_TXT.render(data)
        html_content = TEACHER_VERIFICATION_HTML.render(data)
        send_email(subject, text_content, to_email, html_content=html_content).delay()


@receiver(pre_save, sender=Teacher)
def delete_document_if_verified(sender, instance, **kwargs):
    if instance.verified and instance.verification_file:
        try:
            instance.verification_file.delete(save=False)
            instance.verification_file = None
        except Exception:
            logger.exception("Exception occured while trying to delete verified file")

