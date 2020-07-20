import datetime
import hashlib
import random
import time
import uuid
import requests
import xml.etree.ElementTree as ET
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import urlopen
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField
from moneyed import Money
from apps.core.models import BaseModel
from apps.accounts.models import User, Student, Teacher


class Course(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return self.title

    @property
    def topics(self):
        return self.topic_set.all()


class Topic(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return self.title


class Classroom(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )
    students = models.ManyToManyField(Student)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    attendee_password = models.CharField(max_length=120, null=True)
    moderator_password = models.CharField(max_length=120, null=True)

    started_class = models.BooleanField(default=False)
    starting_class = models.BooleanField(default=False)
    started_class_at = models.DateTimeField(null=True, blank=True)

    finsihed_class = models.BooleanField(default=False)
    finished_class_at = models.DateTimeField(null=True, blank=True)

    max_capacity = models.PositiveIntegerField(default=50)

    def __str__(self):
        return self.name

    @property
    def duration(self):
        if self.started_class_at:
            if self.finished_class_at:
                return self.finished_class_at - self.started_class_at
            else:
                return timezone.now() - self.started_class_at
        else:
            return None

    def build_api_request(self, call, parameters):
        to_hash = call + urlencode(parameters) + settings.BBB_SHARED_SECRET
        h = hashlib.sha1(to_hash.encode("utf-8"))
        parameters["checksum"] = h.hexdigest()
        url = "{}/bigbluebutton/api/".format(settings.BBB_URL)
        request = url + "{}?{}".format(call, urlencode(parameters))
        return request

    def create_classroom(self):
        if not self.starting_class:
            self.starting_class = True
            self.save()
            callback_url = "{}/classrooms/classroom/end/{}".format(
                settings.API_HOST, self.id
            )
            parameters = {
                "allowStartStopRecording": "true",
                "autoStartRecording": "false",
                "logoutURL": settings.HOST,
                "meetingID": str(self.id),
                "meta_endCallbackUrl": callback_url,
                "name": self.name,
                "welcome": "<br>Welcome to <b>{}</b>!".format(settings.SITE_NAME),
            }
            r = self.build_api_request("create", parameters)
            response = urlopen(r).read()
            xml = ET.XML(response)
            returncode = xml.find("returncode").text
            if returncode == "SUCCESS":
                self.attendee_password = xml.find("attendeePW").text
                self.moderator_password = xml.find("moderatorPW").text
                self.started_class = True
                self.starting_class = False
                self.started_class_at = timezone.now()
                self._add_webhook()

            self.save()
        else:
            while self.starting_class:
                time.sleep(0.05)
                self.refresh_from_db(fields=["starting_class"])

    def _add_webhook(self):
        call = "hooks/create"
        parameters = {
            "callbackURL": "{}/classrooms/webhook_callback".format(settings.HOST),
            "meetingID": str(self.id),
        }
        full_link = "{}/bigbluebutton/api/{}?{}".format(
            settings.BBB_URL, call, urlencode(parameters)
        )
        r = requests.get(full_link)

    def create_join_link(self, user, moderator=False):
        if not self.started_class:
            self.create_classroom()

        is_teacher = user == self.teacher
        is_student = user in self.students.all()

        if (is_teacher or is_student) and self.started_class:
            parameters = {
                "fullName": str(user),
                "userID": str(user.id),
                "redirect": "true",
                "meetingID": str(self.id),
                "password": self.moderator_password
                if moderator
                else self.attendee_password,
            }
            return self.build_api_request("join", parameters)

        return None

    def get_meeting_info(self):
        call = "getMeetingInfo"
        parameters = {"meetingID": str(self.id)}
        return requests.get(build_api_request("join", parameters)).content


class Request(BaseModel):
    STATUS = (
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("pending", "Pending"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, null=True, default=None,
    )
    status = models.CharField(max_length=16, choices=STATUS, default="pending")

    class Meta:
        unique_together = [["student", "classroom"]]

    def __str__(self):
        return "{} requested class {}".format(self.student, self.classroom)
