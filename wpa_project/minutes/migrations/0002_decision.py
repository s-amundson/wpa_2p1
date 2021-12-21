# Generated by Django 3.2.4 on 2021-12-20 15:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('minutes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision_date', models.DateField(default=django.utils.timezone.now)),
                ('text', models.TextField()),
            ],
        ),
    ]
