# Generated by Django 5.0.7 on 2025-03-22 17:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0005_alter_staffprofile_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Draft'), (1, 'Publish'), (2, 'Obsolete')], default=0)),
                ('policy', models.TextField()),
                ('is_html', models.BooleanField(default=False)),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.policy')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
