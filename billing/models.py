from django.db import models

from account.models import UserAccount
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.utils import timezone
from diagram.choices import PaymentGatewayChoices
# Create your models here.


class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BillingCycleChoices(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


PRICE_PER_DIAGRAM = 4000


class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    monthly_price = models.IntegerField(default=0)
    diagram_count = models.IntegerField(default=0)
    table_count = models.IntegerField(default=0)
    export = models.BooleanField(
        default=False, help_text="Indicates if users can export diagram"
    )
    team_collaboration = models.BooleanField(default=False)
    live_sync = models.BooleanField(default=False)
    version_control = models.BooleanField(default=False)
    features = models.TextField(help_text="Comma separated list of features")
    popular = models.BooleanField(default=False)
    style_id = models.IntegerField(default=1)
    paystack_plan_code = models.TextField(
        null=True, blank=True, help_text="Plan code of the monthly plan on paystack"
    )
    paystack_yearly_plan_code = models.TextField(
        null=True, blank=True, help_text="Plan code of the yearly plan on paystack"
    )
    stripe_monthly_plan_id = models.TextField(
        null=True, blank=True, help_text="Plan id of the monthly plan on stripe"
    )
    stripe_yearly_plan_id = models.TextField(
        null=True, blank=True, help_text="Plan id of the yearly plan on stripe"
    )
    currency_symbol = models.CharField(default="$", max_length=5)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["monthly_price"]


class Subscription(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    duration = models.IntegerField(help_text="duration in months")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount_paid = models.IntegerField()
    billing_cycle = models.CharField(
        choices=BillingCycleChoices.choices, default=BillingCycleChoices.MONTHLY
    )
    expiry_date = models.DateTimeField()
    customer_code = models.TextField(null=True, blank=True)
    payment_gateway = models.CharField(
        choices=PaymentGatewayChoices.choices, default=PaymentGatewayChoices.PAYSTACK
    )

    @property
    def get_expiry_date(self):
        if self.created_at:
            return self.created_at + relativedelta(months=self.duration)
        else:
            return timezone.now() + relativedelta(months=self.duration)

    @property
    def is_active(self):
        return timezone.now() < self.get_expiry_date

    def save(self, *args, **kwargs):
        self.expiry_date = self.get_expiry_date
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"By {self.user.email} on {self.created_at}"



class TransactionTypeChoices(models.TextChoices):
    SUBSCRIPTION= 'subscription', 'Subscription'
    DIAGRAM_CHARGE = 'diagram_charge', 'Diagram charge'
    
class TransactionStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    
class Transaction(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    trx_reference = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_type = models.CharField(max_length=25, choices=TransactionTypeChoices.choices, default=TransactionTypeChoices.DIAGRAM_CHARGE)
    payload = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=TransactionStatusChoices.choices, default=TransactionStatusChoices.PENDING)