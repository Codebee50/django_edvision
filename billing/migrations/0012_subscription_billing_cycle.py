# Generated by Django 5.1.3 on 2025-04-12 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_plan_paystack_yearly_plan_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='billing_cycle',
            field=models.CharField(choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')], default='monthly'),
        ),
    ]
