# Generated by Django 4.0.5 on 2023-01-15 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_alter_paymenterrorlog_idempotency_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentlog',
            name='volunteer_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='refundlog',
            name='volunteer_points',
            field=models.FloatField(default=0),
        ),
    ]