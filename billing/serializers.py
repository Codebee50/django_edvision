from rest_framework import serializers
from .models import BillingCycleChoices, Plan, Subscription


class SubscribeSerializer(serializers.Serializer):
    plan = serializers.IntegerField()
    billing_cycle = serializers.ChoiceField(choices=BillingCycleChoices.choices)

    def validate_plan(self, value):
        try:
            plan = Plan.objects.get(id=value)
            return plan
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan not found")


class PlanSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = "__all__"

    def get_features_list(self, obj):
        return obj.features.split(",")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    is_active = serializers.SerializerMethodField()
    expiry_date = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = "__all__"

    def get_is_active(self, obj):
        return obj.is_active

    def get_expiry_date(self, obj):
        return obj.get_expiry_date
