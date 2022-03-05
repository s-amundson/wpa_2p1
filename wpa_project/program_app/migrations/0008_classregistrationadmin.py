# Generated by Django 3.2.4 on 2022-03-05 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program_app', '0007_alter_classregistration_reg_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassRegistrationAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('class_registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='program_app.classregistration')),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
