# Generated by Django 4.0.5 on 2022-08-06 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_paymentlog_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
