# Generated by Django 4.0.3 on 2022-05-04 17:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0007_delete_automaticpayment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomaticPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_account', models.CharField(default='undefined', max_length=250)),
                ('value', models.IntegerField()),
                ('description', models.TextField()),
                ('repeat_number', models.IntegerField()),
                ('repeat_time', models.CharField(default='undefined', max_length=250)),
                ('repeat_every', models.IntegerField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank_app.account')),
            ],
        ),
    ]
