# Generated by Django 4.0.3 on 2022-04-30 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0004_alter_bank_bankcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='confirmed',
            field=models.CharField(default='undefined', max_length=100),
        ),
    ]