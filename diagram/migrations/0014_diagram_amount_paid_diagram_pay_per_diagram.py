# Generated by Django 5.1.3 on 2025-04-12 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagram', '0013_alter_databasecolumn_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagram',
            name='amount_paid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='diagram',
            name='pay_per_diagram',
            field=models.BooleanField(default=False),
        ),
    ]
