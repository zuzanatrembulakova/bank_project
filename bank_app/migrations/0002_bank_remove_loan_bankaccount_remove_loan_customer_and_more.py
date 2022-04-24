# Generated by Django 4.0.3 on 2022-04-23 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bankCode', models.IntegerField()),
                ('path', models.CharField(max_length=250)),
            ],
        ),
        migrations.RemoveField(
            model_name='loan',
            name='bankAccount',
        ),
        migrations.RemoveField(
            model_name='loan',
            name='customer',
        ),
        migrations.DeleteModel(
            name='BankAccount',
        ),
        migrations.DeleteModel(
            name='Loan',
        ),
    ]