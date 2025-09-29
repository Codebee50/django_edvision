import json
from multiprocessing import Value
from urllib import response
import uuid
from rest_framework import generics

from account.models import UserAccount
from account.serializers import UserSerializer
from account.utils import notify_user
import billing
from billing.models import (
    BillingCycleChoices,
    Plan,
    Subscription,
    Transaction,
    TransactionTypeChoices,
)
from billing.serializers import (
    PlanSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
)
from rest_framework.permissions import IsAuthenticated

from billing.utils import ApiResponse, convert_dollar_to_naira, get_active_subscription, request_paystack
from common.responses import ErrorResponse, SuccessResponse
from common.utils import format_first_error
from django.conf import settings
from django.db.models import Q

from diagram.choices import PaymentGatewayChoices
from diagram.models import Diagram
import stripe
from rest_framework import status
from django.db.models import Q



class StripeWebhookView(generics.GenericAPIView):
    
    def handle_invoice_payment_succeeded(self, event):
        print("the event is", json.dumps(event, default=str))
        
        session = event.get("data", {}).get("object", {})
        
        #get the plant he user tried to subscribe to
        price_id = session.get("lines").get("data")[0].get("plan").get("id")
        plan = Plan.objects.filter(Q(stripe_monthly_plan_id=price_id) | Q(stripe_yearly_plan_id=price_id)).first()
        if not plan:
            return
        
        
        #get the user who tried to subscribe
        customer_email = session.get("customer_email")
        try:
            user = UserAccount.objects.get(email=customer_email)
        except Exception as e:
            print("an error occurred", e)
            return
        
        #get the billing cycle the user tried to subscribe to
        billing_cycle = BillingCycleChoices.YEARLY if plan.stripe_yearly_plan_id == price_id else BillingCycleChoices.MONTHLY
        duration = 12 if billing_cycle == BillingCycleChoices.YEARLY else 1
        
        #get the amount paid for the subscription in dollars 
        amount_paid = int(session.get("amount_paid")) / 100
        
        #create a subscription
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={
                "plan": plan,
                "duration": duration,
                "amount_paid": amount_paid,
                "billing_cycle": billing_cycle,
                "customer_code": session.get("customer"),
                "payment_gateway": PaymentGatewayChoices.STRIPE,
            }
        )
        
        notify_user(
            user,
            "You are now subscribed to ERDVision",
            f"Welcome to ERDVision!\n\nYour subscription to the {plan.name} plan was successful! You now have full access to the features in {plan.name}. \n\nWe're excited to have you on board, Happy diagramming!",
            send_email=True,
        )
        return True
        

        
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return ErrorResponse(message=str(e))
        except stripe.error.SignatureVerificationError as e:
            return ErrorResponse(message=str(e), status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return ErrorResponse(message=str(e))
        
        if event.get('type') == "invoice.payment_succeeded":
            self.handle_invoice_payment_succeeded(event)
        
        return SuccessResponse(message="OK")
            
            

class PaystackCallbackView(generics.GenericAPIView):
    def diagram_charge_handler(self, charge_data, transaction: Transaction):
        data = charge_data.get("data")
        reference = data.get("reference")

        try:
            amount = int(data.get("amount")) / 100
            diagram_id = uuid.UUID(transaction.payload)
            print("the diaram id", diagram_id)
            diagram = Diagram.objects.get(id=diagram_id)
            diagram.pay_per_diagram = True
            diagram.has_paid = True
            diagram.amount_paid = amount
            diagram.save()

            notify_user(
                diagram.creator,
                "Diagram charge success",
                f"You have successfully paid NGN {amount} for your diagram, you now get lifetime access to all the features in enterprise for this diagram.",
            )
        except Exception as e:
            print("an error occurred", e)

    def subscription_success_handler(self, charge_data):
        data = charge_data.get("data")
        plan_details = data.get("plan")
        customer = data.get("customer")

        try:
            user = UserAccount.objects.get(email=customer.get("email"))

            plan_code = plan_details.get("plan_code")
            plan_interval = plan_details.get("interval")
            amount_paid = int(data.get("amount")) / 100
            plan = Plan.objects.filter(
                Q(paystack_plan_code=plan_code) | Q(paystack_yearly_plan_code=plan_code)
            ).first()
            if not plan:
                return False

            duration = 365 if plan_interval == "annually" else 30
            billing_cycle = (
                BillingCycleChoices.YEARLY
                if plan_interval == "annually"
                else BillingCycleChoices.MONTHLY
            )

            Subscription.objects.create(
                user=user,
                plan=plan,
                duration=duration,
                amount_paid=amount_paid,
                billing_cycle=billing_cycle,
                customer_code=customer.get('customer_code')
            )

            notify_user(
                user,
                "Subscription created successfully",
                "Your subscription was successful! You now have full access to your selected plan. We're excited to have you on board!",
            )

            return True
        except Exception as e:
            print("an error occurred", e)
            return False

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        print("received an event from paystack webhook", payload)
        event_type = payload.get("event")

        if event_type == "charge.success":
            reference = payload.get("data", {}).get("reference", None)
            transaction = Transaction.objects.filter(
                trx_reference=uuid.UUID(reference)
            ).first()
            if transaction:
                transaction_type = transaction.transaction_type
                if transaction_type == TransactionTypeChoices.SUBSCRIPTION:
                    self.subscription_success_handler(payload)
                if transaction_type == TransactionTypeChoices.DIAGRAM_CHARGE:
                    self.diagram_charge_handler(payload, transaction)

        return SuccessResponse(message="success")


class SubscribeToPlanView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer
    
    def initiate_paystack_subscription(self, callback_url, plan, user, billing_cycle):
        plan_code_key = ("paystack_plan_code"if billing_cycle == BillingCycleChoices.MONTHLY else "paystack_yearly_plan_code")
        plan_code = getattr(plan, plan_code_key, None)
        print("the plan code is", plan_code)
        if not plan_code:
            return ErrorResponse(message="Plan not configured, please try gain later")
        
        
        reference = str(uuid.uuid4())
        request_body = {
            "email": user.email,
            "amount": plan.monthly_price,
            "plan": plan_code,
            "callback_url": callback_url,
            "reference": reference,
        }
        response = request_paystack("/transaction/initialize", method="post", data=request_body)
        if response.error:
            return ApiResponse(error=True, message=response.message)
   
        Transaction.objects.create(
            user=user,
            trx_reference=reference,
            transaction_type=TransactionTypeChoices.SUBSCRIPTION,
        )
        return ApiResponse(error=False, body=response.body, message=response.message)
    
    def initiate_stripe_subscription(self, callback_url, plan, user, billing_cycle):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        plan_code_key = "stripe_monthly_plan_id" if billing_cycle == BillingCycleChoices.MONTHLY else "stripe_yearly_plan_id"
        plan_code = getattr(plan, plan_code_key, None)
        print("the plan code is", plan_code)
        if not plan_code:
            return ApiResponse(error=True, message="Plan not configured, please try gain later")
        try:
            reference = str(uuid.uuid4())
            session = stripe.checkout.Session.create(
                success_url=callback_url,
                cancel_url=callback_url,
                mode="subscription",
                customer_email=user.email,
                line_items=[{
                    "price": plan_code,
                    "quantity": 1,
                }],
                metadata={
                    "reference": reference,
                    "plan_id": str(plan.id),
                    "user_id": str(user.id),
                },
            )
            
            response_body = {
                "data": {
                    "authorization_url": session.url,
                    "reference": reference,
                    "session_id": session.id,
                }
            }
            
            Transaction.objects.create(
                user=user,
                trx_reference=reference,
                transaction_type=TransactionTypeChoices.SUBSCRIPTION,
            )
            
            return ApiResponse(error=False, body=response_body, message="Subscription initialized")
        except Exception as e:
            return ApiResponse(error=True, message=str(e))

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))

        plan = serializer.validated_data.get("plan")
        billing_cycle = serializer.validated_data.get("billing_cycle")
        
        active_subscription = get_active_subscription(request.user)
        if active_subscription and active_subscription.is_active:
            if active_subscription.plan.monthly_price >= plan.monthly_price:
                return ErrorResponse(message=f"You are already subscribed to the {active_subscription.plan.name} plan")
            
            
        if plan.monthly_price == 0:
            # crate a 1 year free plan
            subscription = Subscription.objects.create(
                user=request.user,
                duration=12,
                plan=plan,
                amount_paid=0,
                billing_cycle=BillingCycleChoices.YEARLY,
            )
            return SuccessResponse(
                message="User subscribed successfully",
                data={
                    "user_subscribed": True,
                    "subscription": SubscriptionSerializer(subscription).data,
                    "user": UserSerializer(request.user).data,
                },
            )
        user = request.user        
        callback_url = f"{settings.FE_URL}/dashboard"
        response = self.initiate_stripe_subscription(callback_url, plan, user, billing_cycle)
        # response = self.initiate_paystack_subscription(callback_url, plan, user, billing_cycle)
        if response.error:
            return ErrorResponse(message=response.message)

        return SuccessResponse(message="Subscription initialized", data=response.body)


class GetPlans(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
