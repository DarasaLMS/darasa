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


@shared_task
def schedule_meetings():
    print("Schedule meetings")
    # Cancel requests past classroom schedule datetime
    # 10min before class. Go through all approved requests and create meeting
    # Thereafter, create join link and email to all users (teacher and students)
    # Send email to rejected requests and create meeting
