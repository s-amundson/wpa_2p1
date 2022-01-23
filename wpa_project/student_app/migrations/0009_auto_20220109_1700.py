# Generated by Django 3.2.4 on 2022-01-10 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_app', '0008_student_covid_vax'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='signature',
            field=models.ImageField(null=True, upload_to='signatures/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='student',
            name='signature_pdf',
            field=models.FileField(null=True, upload_to='signatures/%Y/%m/%d/'),
        ),
    ]