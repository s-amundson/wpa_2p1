# Generated by Django 3.2.4 on 2022-06-24 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20220619_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentlog',
            name='category',
            field=models.CharField(choices=[('donation', 'Donation'), ('intro', 'Introductory Class'), ('joad', 'JOAD'), ('membership', 'Membership')], default='intro', max_length=50),
        ),
    ]