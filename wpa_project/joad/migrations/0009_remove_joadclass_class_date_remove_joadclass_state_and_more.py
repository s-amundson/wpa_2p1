# Generated by Django 4.0.5 on 2022-12-06 04:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('joad', '0008_rename_event_eventregistration_joad_event_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joadclass',
            name='class_date',
        ),
        migrations.RemoveField(
            model_name='joadclass',
            name='state',
        ),
        migrations.RemoveField(
            model_name='joadevent',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='joadevent',
            name='event_date',
        ),
        migrations.RemoveField(
            model_name='joadevent',
            name='state',
        ),
    ]
