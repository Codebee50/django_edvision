from django.db import models

from account.models import UserAccount

# Create your models here.


class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    monthly_price= models.IntegerField(default=0)
    diagram_count = models.IntegerField(default=0)
    table_count = models.IntegerField(default=0)
    export = models.BooleanField(default=False, help_text="Indicates if users can export diagram")
    team_collaboration= models.BooleanField(default=False)
    live_sync = models.BooleanField(default=False)
    version_control= models.BooleanField(default=False)
    features = models.TextField(help_text="Comma separated list of features")
    popular = models.BooleanField(default=False)
    style_id = models.IntegerField(default=1)
    paystack_plan_code = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['monthly_price']

class Subscription(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.BooleanField)
    duration = models.IntegerField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount_paid = models.IntegerField()
    
