# Generated by Django 4.0.5 on 2023-01-08 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_registration_volunteerevent_registrationadmin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteerrecord',
            name='volunteer_points',
            field=models.FloatField(default=0),
        ),
    ]
