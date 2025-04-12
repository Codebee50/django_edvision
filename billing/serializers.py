from rest_framework import serializers
from .models import Plan


class SubscribeSerializer(serializers.Serializer):
    plan = serializers.IntegerField()
    
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
        return obj.features.split(',')
