# Generated by Django 5.1.3 on 2025-04-12 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0008_plan_paystack_plan_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='currency_symbol',
            field=models.CharField(default='₦', max_length=5),
        ),
    ]
