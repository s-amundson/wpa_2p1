# Generated by Django 4.0.5 on 2022-10-15 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact_us', '0007_alter_email_created_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
