# Generated by Django 3.2.4 on 2021-09-12 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_app', '0005_alter_student_student_family'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(default=None, max_length=254, null=True),
        ),
    ]