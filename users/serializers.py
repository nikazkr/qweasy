from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, Profile


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role", "status", "total_tests_taken", "total_time_spent",
                  "overall_percentage")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize registration requests and create a new user.
    """

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "role")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer class to authenticate users with email and password.
    """

    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class ProfileSerializer(CustomUserSerializer):
    """
    Serializer class to serialize the user Profile model
    """

    class Meta:
        model = Profile
        fields = ("bio", "birth_date", "gender", "first_name", "last_name", "level")


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the avatar
    """

    class Meta:
        model = Profile
        fields = ("avatar",)


class StatusChangeSerializer(serializers.Serializer):
    accept = serializers.BooleanField()
