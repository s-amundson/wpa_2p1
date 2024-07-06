# Generated by Django 5.0.2 on 2024-04-28 21:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0008_election_description_election_election_close_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='description',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='election_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
