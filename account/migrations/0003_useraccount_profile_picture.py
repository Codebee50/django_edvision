# Generated by Django 5.1.3 on 2024-11-30 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_useraccount_is_admin_useraccount_is_staff_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile-images/'),
        ),
    ]
