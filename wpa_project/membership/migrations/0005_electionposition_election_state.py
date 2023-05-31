# Generated by Django 4.0.5 on 2023-02-25 23:14

from django.db import migrations, models

def insert_position_data(apps, schema_editor):
    # copy the event data from the beginner class table to the event table
    ep = apps.get_model('membership', 'ElectionPosition')
    positions = ['President', 'Vice President', 'Secretary', 'Treasurer', 'Member at Large']
    for p in positions:
        ep.objects.create(position=p)

class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0004_election_electioncandidate_electionvote'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElectionPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='election',
            name='state',
            field=models.CharField(choices=[('scheduled', 'scheduled'), ('open', 'open'), ('closed', 'closed')], max_length=20, null=True),
        ),
        migrations.RunPython(insert_position_data),
    ]
