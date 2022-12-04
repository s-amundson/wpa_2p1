# Generated by Django 4.0.5 on 2022-12-04 01:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    def copy_event_data(apps, schema_editor):
        # copy the event data from the beginner class table to the event table
        jc = apps.get_model('joad', 'JoadClass')
        je = apps.get_model('joad', 'JoadEvent')
        event = apps.get_model('event', 'Event')

        for c in jc.objects.all().order_by('id'):
            c.event = event.objects.create(
                event_date=c.class_date,
                state=c.state,
                type='joad class'
            )
            c.save()

        for c in je.objects.all().order_by('id'):
            c.event = event.objects.create(
                event_date=c.event_date,
                cost_standard=c.cost,
                cost_member=c.cost,
                state=c.state,
                type='joad event'
            )
            c.save()

    dependencies = [
        ('event', '0003_alter_event_type'),
        ('joad', '0007_auto_20220228_1900'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventregistration',
            old_name='event',
            new_name='joad_event',
        ),
        migrations.AddField(
            model_name='joadclass',
            name='event',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.event'),
        ),
        migrations.AddField(
            model_name='joadevent',
            name='event',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.event'),
        ),
        migrations.RunPython(copy_event_data),
    ]