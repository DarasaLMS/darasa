"""
Authentication Backend Override
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

USER = get_user_model()


class AuthenticationBackend(ModelBackend):
    """
    Authenticates Users
    """

    def authenticate(self, **credentials):
        """Authenticate action

        Authenticate user's email against the given password
        """
        # Login credentials
        email = credentials.get("email")
        pwd_valid = credentials.get("password")

        if email and pwd_valid:
            try:
                user = USER.objects.get(
                    Q(email__iexact=email)
                    | Q(username__iexact=email)
                    | Q(phone__iexact=email)
                )
            except USER.DoesNotExist:
                return None

            if user.check_password(pwd_valid):
                return user
