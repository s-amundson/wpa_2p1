# Generated by Django 3.2.4 on 2022-01-07 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_paymenterrorlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenterrorlog',
            name='error_count',
            field=models.IntegerField(default=0),
        ),
    ]
