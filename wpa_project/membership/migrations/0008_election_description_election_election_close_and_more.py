# Generated by Django 5.0.2 on 2024-04-28 03:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0007_remove_electionvote_at_large_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='description',
            field=models.CharField(default='General Election', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='election',
            name='election_close',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='electionvote',
            name='member_at_large',
            field=models.ManyToManyField(limit_choices_to={'position': 5}, related_name='at_large_candidate', to='membership.electioncandidate'),
        ),
        migrations.CreateModel(
            name='ElectionNotificationDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_date', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='scheduled', max_length=20)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='membership.election')),
            ],
        ),
    ]
