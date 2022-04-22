# Generated by Django 4.0.3 on 2022-04-22 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0004_delete_loan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loanAmount', models.IntegerField()),
                ('remainingAmount', models.IntegerField()),
                ('confirmed', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank_app.account')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank_app.customer')),
            ],
        ),
    ]
