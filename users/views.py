import os

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.permissions import IsSensei
from utils.token import create_custom_token
from .models import Profile, CustomUser
from .serializers import CustomUserSerializer, StatusChangeSerializer, UserRegistrationSerializer, UserLoginSerializer, \
    ProfileSerializer, ProfileAvatarSerializer

User = get_user_model()


class UserRegistrationAPIView(GenericAPIView):
    """
    An endpoint for the client to create a new User.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = create_custom_token(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = self.serializer_class(user)
        token = create_custom_token(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class UserAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user information
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class UserAvatarAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileAvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


@extend_schema(
    examples=[
        OpenApiExample(
            'Example',
            value={
                'code': 'string',
                'role': 'string',
            },
        ),
    ]
)
class CustomGoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.environ.get('CALLBACK_URL')
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = self.user
            role = request.data.get('role', 'noob')
            if role not in ['noob', 'sensei']:
                raise ValidationError('Invalid role!')
            user.role = role
            user.save()
            token = create_custom_token(user)
            response.data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return response


class StatusChangeView(APIView):
    serializer_class = StatusChangeSerializer
    permission_classes = (IsAdminUser,)

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if user.status != "pending":
            return Response({"message": "User status is not pending"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            accept = serializer.validated_data.get('accept')
            if accept:
                user.status = "accepted"
                message = "Status change accepted"
            else:
                user.status = "declined"
                message = "Status change declined"

            user.save()
            return Response({"message": message}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendStatusChangeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.user.role != "sensei":
            return Response({"message": "Only senseis can request status change"}, status=status.HTTP_403_FORBIDDEN)
        else:
            request.user.status = "pending"
            request.user.save()
            return Response({"message": "Status change request resent"}, status=status.HTTP_200_OK)


class UsersListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminUser, IsSensei)
