from re import sub
from rest_framework import serializers

from billing.models import Subscription
from billing.serializers import SubscriptionSerializer
from billing.utils import get_active_subscription
from .models import Notification, UserAccount
from django.utils import timezone


class NotificationIdSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Notification


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = "__all__"

    def get_active_subscription(self, obj):
        subscription = get_active_subscription(obj)
        if subscription:
            return SubscriptionSerializer(subscription).data
        return None


class UserFieldsSerializer(serializers.ModelSerializer):
    active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = [
            "first_name",
            "last_name",
            "email",
            "active_subscription",
            "profile_picture",
            'id'
        ]

    def get_active_subscription(self, obj):
        subscription = get_active_subscription(obj)
        if subscription:
            return SubscriptionSerializer(subscription).data
        return None


class EmailOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not UserAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exist")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegistrationSerializer(serializers.ModelSerializer):
    invitation = serializers.IntegerField(required=False)

    class Meta:
        model = UserAccount
        fields = ["first_name", "last_name", "email", "password", "invitation"]
