# Generated by Django 3.0.5 on 2021-04-24 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsetmc', '0003_auto_20210424_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrumentpricedata',
            name='turnover',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='instrumentpricedata',
            name='valueOfTransactions',
            field=models.BigIntegerField(),
        ),
    ]
