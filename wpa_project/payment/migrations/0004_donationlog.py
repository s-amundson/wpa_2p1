# Generated by Django 3.2.4 on 2022-03-01 03:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_paymenterrorlog_error_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('note', models.TextField()),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.paymentlog')),
            ],
        ),
    ]