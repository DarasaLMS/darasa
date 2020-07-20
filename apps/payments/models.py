import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from djmoney.models.fields import MoneyField
from moneyed import Money
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.classrooms.models import Classroom, Course


class Billing(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=256, blank=True)
    address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=256, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    country_area = models.CharField(max_length=256, blank=True)

    cc_first_digits = models.CharField(max_length=6, blank=True, default="")
    cc_last_digits = models.CharField(max_length=4, blank=True, default="")
    cc_brand = models.CharField(max_length=40, blank=True, default="")
    cc_exp_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    cc_exp_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1000)], null=True, blank=True
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.address_1, self.user)

    def payments(self):
        return self.payment_set.all()


class Payment(BaseModel):
    CHARGE_STATUS = (
        ("not-charged", "Not charged"),
        ("partially-charged", "Partially charged"),
        ("fully-charged", "Fully charged"),
        ("partially-refunded", "Partially refunded"),
        ("fully-refunded", "Fully refunded"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.PROTECT)
    customer_ip_address = models.GenericIPAddressField(blank=True, null=True)
    transaction_reference = models.CharField(max_length=128, unique=True)
    total_amount = MoneyField(
        max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY
    )
    captured_amount = MoneyField(
        max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY
    )
    charge_status = models.CharField(
        max_length=20, choices=CHARGE_STATUS, default="not-charged"
    )
    extra_data = models.TextField(blank=True, default="")

    def __str__(self):
        return "{}".format(self.transaction_reference)


class Rate(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, null=True, blank=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    price = MoneyField(
        max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY
    )

    def __str__(self):
        return "{}: {}".format(self.course, self.price)
