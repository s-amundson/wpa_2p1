# Generated by Django 3.2.4 on 2022-03-01 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joad', '0006_joadevent_pin_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pinattendance',
            name='bow',
            field=models.CharField(choices=[('', 'None'), ('barebow', 'Barebow/Basic Compound'), ('recurve', 'Recurve/Para Recurve Open'), ('compound', 'Compound/Para Compound Open/W1/Fixed Pins**')], max_length=45),
        ),
        migrations.AlterField(
            model_name='pinscores',
            name='bow',
            field=models.CharField(choices=[('', 'None'), ('barebow', 'Barebow/Basic Compound'), ('recurve', 'Recurve/Para Recurve Open'), ('compound', 'Compound/Para Compound Open/W1/Fixed Pins**')], max_length=45),
        ),
    ]