import re

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, UserRole


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "email",
            "name",
            "role",
            "language",
            "phone",
            "photo_url",
            "is_banned",
            "email_verified",
            "subscription",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_banned",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        if full_name:
            return full_name
        if obj.user.first_name:
            return obj.user.first_name
        return obj.user.email.split("@")[0]

    def get_subscription(self, obj):
        subscription = getattr(obj.user, "subscription", None)
        if subscription:
            return subscription.plan
        return "free"


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=UserRole.choices)

    def validate_email(self, value):
        email = value.lower().strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise serializers.ValidationError("Invalid email format")
        return email

    def validate_name(self, value):
        name = value.strip()
        if len(name) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁәғқңөұүіһӘҒҚҢӨҰҮІҺ\s\-\.]+$', name):
            raise serializers.ValidationError("Name contains invalid characters")
        return name


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SetLanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["kk", "ru", "en"])


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()