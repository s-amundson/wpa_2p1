# Generated by Django 4.2.1 on 2023-07-04 20:58

from django.db import migrations, models
import django.db.models.deletion
import payment.models.reimbursement


class Migration(migrations.Migration):

    dependencies = [
        ('student_app', '0012_user_theme'),
        ('payment', '0010_paymentlog_volunteer_points_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reimbursement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('paid', 'paid'), ('denied', 'denied')], default='pending', max_length=50)),
                ('title', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='student_app.student')),
            ],
        ),
        migrations.CreateModel(
            name='ReimbursementVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approve', models.BooleanField(default=False)),
                ('reimbursement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.reimbursement')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='student_app.student')),
            ],
        ),
        migrations.CreateModel(
            name='ReimbursementItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('description', models.CharField(max_length=100)),
                ('attachment', models.FileField(upload_to=payment.models.reimbursement.attachment_name)),
                ('reimbursement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.reimbursement')),
            ],
        ),
    ]