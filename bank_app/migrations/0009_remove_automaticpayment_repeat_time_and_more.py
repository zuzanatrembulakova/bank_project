# Generated by Django 4.0.3 on 2022-05-04 18:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0008_automaticpayment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='automaticpayment',
            name='repeat_time',
        ),
        migrations.AlterField(
            model_name='automaticpayment',
            name='repeat_every',
            field=models.IntegerField(help_text='how often should we repeat payment (in minutes)'),
        ),
        migrations.AlterField(
            model_name='automaticpayment',
            name='repeat_number',
            field=models.IntegerField(help_text='number of payment repeats'),
        ),
        migrations.AlterField(
            model_name='automaticpayment',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='time of last payment'),
        ),
    ]
