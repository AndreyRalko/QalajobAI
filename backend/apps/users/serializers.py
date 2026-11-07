from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
        allow_blank=True,
    )
    login = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
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

    def get_login(self, obj):
        from apps.users.identity import get_user_login

        return get_user_login(obj.user)

    def get_first_name(self, obj):
        from apps.users.identity import get_user_first_name

        return get_user_first_name(obj.user)

    def get_last_name(self, obj):
        from apps.users.identity import get_user_last_name

        return get_user_last_name(obj.user)

    def get_name(self, obj):
        from apps.users.identity import get_user_full_name, get_user_login

        full_name = get_user_full_name(obj.user)
        if full_name:
            return full_name
        return get_user_login(obj.user)

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