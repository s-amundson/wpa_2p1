# Generated by Django 5.0.2 on 2024-04-28 03:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0004_staffprofile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staffprofile',
            options={'ordering': ['-student__user__is_board']},
        ),
    ]
