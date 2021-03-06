# Generated by Django 3.2.4 on 2021-09-06 00:31

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateField(default=django.utils.timezone.now)),
                ('business', models.TextField()),
                ('resolved', models.DateField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Minutes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_date', models.DateField(default=django.utils.timezone.now)),
                ('start_time', models.TimeField(default=django.utils.timezone.now)),
                ('attending', models.CharField(max_length=250)),
                ('minutes_text', models.CharField(max_length=250)),
                ('memberships', models.IntegerField()),
                ('balance', models.IntegerField(default=None, null=True)),
                ('discussion', models.TextField()),
                ('end_time', models.TimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(choices=[('president', 'President'), ('vice', 'Vice'), ('secretary', 'Secretary'), ('treasure', 'Treasure')], max_length=50)),
                ('report', models.TextField()),
                ('minutes', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='minutes.minutes')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', models.DateField(default=django.utils.timezone.now)),
                ('update_text', models.TextField()),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='minutes.business')),
            ],
        ),
        migrations.AddField(
            model_name='business',
            name='minutes',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='minutes.minutes'),
        ),
    ]
