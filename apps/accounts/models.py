import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.apps import apps
from django.conf import settings
from django.core import validators
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save
from sorl.thumbnail import ImageField
from timezone_field import TimeZoneField
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.tasks import send_email

EMAIL_VERIFICATION_TXT = get_template("emails/email_verification.txt")
EMAIL_VERIFICATION_HTML = get_template("emails/email_verification.html")

PASSWORD_RESET_TXT = get_template("emails/password_reset.txt")
PASSWORD_RESET_HTML = get_template("emails/password_reset.html")


def get_unique_random_string(length=32):
    return get_random_string(length=length)


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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("role", "staff")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model represents a person interacting with the system
    """

    STAFF = "staff"
    STUDENT = "student"
    TEACHER = "teacher"
    ROLES = ((STAFF, _("Staff")), (STUDENT, _("Student")), (TEACHER, _("Teacher")))

    MALE = "male"
    FEMALE = "female"
    GENDERS = ((MALE, _("Male")), (FEMALE, _("Female")))

    MR = "mr"
    MRS = "mrs"
    MISS = "miss"
    MS = "ms"
    DR = "dr"
    PROF = "prof"
    TITLES = (
        (MR, _("Mr")),
        (MRS, _("Mrs")),
        (MISS, _("Miss")),
        (MS, _("Ms")),
        (DR, _("Dr")),
        (PROF, _("Professor")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        _("title"), max_length=16, null=True, blank=True, choices=TITLES
    )
    first_name = models.CharField(_("first name"), max_length=32, blank=True)
    last_name = models.CharField(_("last name"), max_length=32, blank=True)
    nickname = models.CharField(_("display name"), max_length=32, blank=True)
    gender = models.CharField(_("gender"), max_length=8, blank=True, choices=GENDERS)
    email = models.EmailField(_("email address"), unique=True, blank=False, null=False)
    email_verified = models.BooleanField(_("email verified"), default=False)
    phone = PhoneNumberField(_("phone number"), blank=True)
    picture = ImageField(
        upload_to="pictures/%Y/%m", default="pictures/default/user.png"
    )
    calendar = models.OneToOneField(
        "timetable.Calendar", on_delete=models.SET_NULL, null=True, blank=True
    )
    accepted_terms = models.BooleanField(
        _("accepted terms and conditions"), default=False
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    role = models.CharField(_("role"), max_length=16, choices=ROLES, default=STUDENT)

    date_joined = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    timezone = TimeZoneField(
        default="Africa/Nairobi", choices_display="WITH_GMT_OFFSET"
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    _email = None

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email = self.email

    def send_verification_email(self):
        if not self.email_verified:
            token = VerificationToken.objects.get_or_create(user=self)[0]
            subject = _("Welcome to") + " {}".format(settings.SITE_NAME)
            to_email = self.email
            data = {
                "first_name": self.first_name,
                "verification_url": "{}/account-verified/?token={}".format(
                    settings.HOST, str(token.token)
                ),
                "site_name": settings.SITE_NAME,
            }
            text_content = EMAIL_VERIFICATION_TXT.render(data)
            html_content = EMAIL_VERIFICATION_HTML.render(data)
            send_email.delay(subject, text_content, to_email, html_content=html_content)
            return True

        return False

    def check_email_verification(self, token):
        if not hasattr(self, "verificationtoken"):
            return False

        if str(self.verificationtoken.token) == str(token):
            self.email_verified = True
            self.verificationtoken.delete()
            self.save()
            return True
        else:
            return False

    def send_password_reset_email(self):
        PasswordResetToken.objects.filter(user=self).delete()
        pwd_reset_token = PasswordResetToken(user=self)
        pwd_reset_token.save()
        text = _("Reset Password")
        subject = "{}: {}".format(settings.SITE_NAME, text)
        to_email = self.email
        data = {
            "first_name": self.first_name,
            "email": self.email,
            "reset_url": "{}/new-password?token={}".format(
                settings.HOST, pwd_reset_token.token
            ),
            "site_name": settings.SITE_NAME,
        }
        text_content = PASSWORD_RESET_TXT.render(data)
        html_content = PASSWORD_RESET_HTML.render(data)
        send_email.delay(subject, text_content, to_email, html_content=html_content)


@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    if instance.role == instance.STAFF:
        instance.is_staff = True

    # If email has changed
    if instance._email.lower() != instance.email.lower():
        instance.email_verified = False


@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.STUDENT:
            student_model = apps.get_model("schools", "student")
            student_model.objects.get_or_create(user=instance)

        elif instance.role == User.TEACHER:
            teacher_model = apps.get_model("schools", "teacher")
            teacher_model.objects.get_or_create(user=instance)

        # Send account verification email
        instance.send_verification_email()

    if not instance.calendar:
        # Create a user's calendar
        calendar_model = apps.get_model("timetable", "calendar")
        calendar = calendar_model.objects.get_or_create_calendar_for_object(
            instance, name="{}'s Calendar".format(instance.first_name)
        )
        instance.calendar = calendar
        instance.save()


class VerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(
        max_length=32, default=get_unique_random_string, editable=False, unique=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def __str__(self):
        return "{}".format(self.token)


class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(
        max_length=32, default=get_unique_random_string, editable=False, unique=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def __str__(self):
        return "{}".format(self.token)
