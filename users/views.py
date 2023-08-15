from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):  # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/users/login/google'
    client_class = OAuth2Client

# from django.contrib.auth import get_user_model
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
#
# from .serializers import UserSerializer
#
# User = get_user_model()
#
#
# class RegistrationView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#
#             refresh = RefreshToken.for_user(user)
#             tokens = {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#
#             return Response({'user': serializer.data, 'tokens': tokens}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
