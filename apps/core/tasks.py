import time
from hashlib import md5
from celery import task
from celery.utils.log import get_task_logger
from contextlib import contextmanager
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@task(bind=True)
def send_email(
    self,
    subject,
    text_content,
    to_email,
    from_email=settings.DEFAULT_FROM_EMAIL,
    html_content=None,
):
    text_content_hexdigest = md5(text_content.encode(encoding="UTF-8")).hexdigest()
    lock_id = "{0}-lock-{1}".format(self.name, text_content_hexdigest)
    logger.debug("Sending email to %s", to_email)
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, to_email.split(",")
            )
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            msg.send()
    logger.debug("Email to %s is already being sent by another worker", to_email)
