# Generated by Django 5.1.3 on 2025-04-12 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0007_alter_plan_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='paystack_plan_code',
            field=models.TextField(blank=True, null=True),
        ),
    ]
