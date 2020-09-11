from django.contrib import admin
from .models import Billing, Payment, Rate


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    model = Billing
    list_display = (
        "user",
        "address_1",
        "postal_code",
        "city",
        "country",
        "active",
        "date_modified",
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = (
        "transaction_reference",
        "course",
        "billing",
        "customer_ip_address",
        "total_amount",
        "captured_amount",
        "charge_status",
        "date_modified",
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    model = Rate
    list_display = ("course", "price", "date_modified")
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
