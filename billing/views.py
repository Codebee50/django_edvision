from rest_framework import generics

from billing.models import Plan
from billing.serializers import PlanSerializer, SubscribeSerializer
from rest_framework.permissions import IsAuthenticated

from common.responses import ErrorResponse
from common.utils import format_first_error


class SubscribeToPlanView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))
        
        plan = serializer.validated_data.get('plan')
        if not plan.paystack_plan_code:
            return ErrorResponse(message="Plan not configured, please try gain later")
        
        user = request.user 
        


class GetPlans(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
