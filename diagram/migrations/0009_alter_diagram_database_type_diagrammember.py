# Generated by Django 5.1.3 on 2025-01-30 04:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagram', '0008_relationship_from_rel_relationship_to_rel'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagram',
            name='database_type',
            field=models.CharField(choices=[('postgresql', 'PostgreSQL'), ('mysql', 'MySQL'), ('sqlite', 'SQLite'), ('oracle', 'oracle'), ('djangoorm', 'Django orm')], default='postgresql', max_length=20),
        ),
        migrations.CreateModel(
            name='DiagramMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('diagram', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diagram.diagram')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
