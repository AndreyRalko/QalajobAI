from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
        allow_blank=True,
    )
    login = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )
    date_joined = serializers.DateTimeField(
        source="user.date_joined",
        read_only=True,
    )
    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True,
    )
    name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "login",
            "email",
            "name",
            "first_name",
            "last_name",
            "role",
            "language",
            "phone",
            "photo_url",
            "is_banned",
            "is_active",
            "email_verified",
            "student_id",
            "subscription",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "login",
            "email",
            "student_id",
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
        return obj.user.username

    def get_subscription(self, obj):
        subscription = getattr(obj.user, "subscription", None)
        if subscription:
            return subscription.plan
        return "free"


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_login(self, value):
        login = value.strip()
        if not login:
            raise serializers.ValidationError("Login is required")
        return login


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