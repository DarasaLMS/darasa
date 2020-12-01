import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from moneyed import Money
from djmoney.models.fields import MoneyField
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.schools.models import Course


class Billing(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=256, blank=True)
    address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    state = models.CharField(max_length=250, blank=True)
    postal_code = models.CharField(max_length=256, blank=True)
    country = CountryField(blank=True, null=True)

    # Mobile money phone number
    phone = PhoneNumberField(_("Mobile money phone number"), blank=True)

    # Credit card details
    cc_first_digits = models.CharField(max_length=6, blank=True, default="")
    cc_last_digits = models.CharField(max_length=4, blank=True, default="")
    cc_brand = models.CharField(max_length=40, blank=True, default="")
    cc_exp_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    cc_exp_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1000)], null=True, blank=True
    )
    active = models.BooleanField(default=False)

    def __str__(self):
        return "{} : {} {} {} {}".format(
            self.user, self.address_1, self.postal_code, self.city, self.country
        )

    def payments(self):
        return self.payment_set.all()


class Payment(BaseModel):
    NOT_CHARGED = "not-charged"
    PARTIALLY_CHARGED = "partially-charged"
    FULLY_CHARGED = "fully-charged"
    PARTIALLY_REFUNDED = "partially-refunded"
    FULLY_REFUNDED = "fully-refunded"

    CHARGE_STATUS = (
        (NOT_CHARGED, "Not charged"),
        (PARTIALLY_CHARGED, "Partially charged"),
        (FULLY_CHARGED, "Fully charged"),
        (PARTIALLY_REFUNDED, "Partially refunded"),
        (FULLY_REFUNDED, "Fully refunded"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
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
        max_length=20, choices=CHARGE_STATUS, default=NOT_CHARGED
    )
    extra_data = models.TextField(blank=True, default="")

    def __str__(self):
        return "{}".format(self.transaction_reference)


class Rate(BaseModel):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, primary_key=True)
    price = MoneyField(
        max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY
    )

    def __str__(self):
        return "{}: {}".format(self.course, self.price)
