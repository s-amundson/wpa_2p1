# Generated by Django 4.2.1 on 2023-07-17 15:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_reimbursement_modified_reimbursementvote_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='reimbursement',
            name='note',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='reimbursement',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]