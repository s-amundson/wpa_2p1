# Generated by Django 5.0.2 on 2024-05-28 20:30

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact_us', '0009_email_ip'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('services', 'services'), ('harassment', 'harassment'), ('website', 'website')], max_length=20, null=True)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('incident_date', models.DateField(default=None, null=True)),
                ('message', models.TextField()),
                ('resolved_date', models.DateTimeField(default=None, null=True)),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ComplaintComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('comment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contact_us.complaint')),
            ],
        ),
    ]
