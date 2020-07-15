from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.api.serializers import LoginSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
