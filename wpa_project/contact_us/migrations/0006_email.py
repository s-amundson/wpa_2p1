# Generated by Django 4.0.5 on 2022-10-13 22:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contact_us', '0005_message_spam_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_valid', models.BooleanField(default=True)),
            ],
        ),
    ]
