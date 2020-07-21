from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email(
    subject,
    text_content,
    to_email,
    from_email=settings.DEFAULT_FROM_EMAIL,
    html_content=None,
):
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email.split(","))
    if html_content:
        msg.attach_alternative(html_content, "text/html")
    msg.send()
