# Generated by Django 5.0.7 on 2025-04-06 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0008_article_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='access',
            field=models.CharField(choices=[('public', 'Public'), ('members', 'Members'), ('staff', 'Staff'), ('board', 'Board')], default='public', max_length=40),
        ),
    ]
