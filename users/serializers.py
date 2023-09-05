from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import CustomUser
from rest_framework.authtoken.models import Token


class CustomRegisterSerializer(RegisterSerializer):
    role = serializers.ChoiceField(choices=CustomUser.Role)
    level = serializers.ChoiceField(choices=CustomUser.Level, required=False)
    gender = serializers.ChoiceField(choices=CustomUser.Gender, required=False)
    age = serializers.IntegerField(required=False)

    def custom_signup(self, request, user):
        user.role = self.validated_data.get('role')
        user.level = self.validated_data.get('level')
        user.gender = self.validated_data.get('gender')
        user.age = self.validated_data.get('age')
        user.save()

        # Generate a token for the registered user
        token, _ = Token.objects.get_or_create(user=user)
        return token
