# Generated by Django 5.0.7 on 2024-07-28 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0003_rename_time_posts_created_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='post_id',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]