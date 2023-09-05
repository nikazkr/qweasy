from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import CustomRegisterSerializer


class GoogleLogin(SocialLoginView):  # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/users/login/google'
    client_class = OAuth2Client


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
