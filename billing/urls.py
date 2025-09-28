from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.GetPlans.as_view(), name='get-plans-list'),
    path('subscribe/', views.SubscribeToPlanView.as_view(), name='subscribe-to-plan'),
    path('paystack/callback/', views.PaystackCallbackView.as_view(), name='paystack-callback'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe-callback'),
]