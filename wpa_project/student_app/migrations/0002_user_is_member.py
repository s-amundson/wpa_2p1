# Generated by Django 3.2.4 on 2021-09-04 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_member',
            field=models.BooleanField(default=False),
        ),
    ]
