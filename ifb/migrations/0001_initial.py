# Generated by Django 3.0.5 on 2021-04-17 14:16

import django.core.validators
from django.db import migrations, models
import django_mysql.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IFBInstrument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ifb_url', models.URLField(max_length=300, validators=[django.core.validators.URLValidator])),
                ('symbolFa', models.CharField(max_length=50)),
                ('companyFA', models.CharField(max_length=100)),
                ('mnemonic', models.CharField(max_length=50)),
                ('companyEN', models.CharField(max_length=100)),
                ('isin', models.CharField(max_length=50)),
                ('market', models.CharField(blank=True, max_length=50, null=True)),
                ('industry', models.CharField(blank=True, max_length=50, null=True)),
                ('subIndustry', models.CharField(max_length=50)),
                ('parValue', models.IntegerField()),
                ('totalCount', models.IntegerField()),
                ('listedCount', models.IntegerField()),
                ('settlementDate', models.DateField()),
                ('publishDate', models.DateField()),
                ('subject', models.CharField(max_length=100)),
                ('nominalReturnRate', models.SmallIntegerField()),
                ('couponPeriod', models.SmallIntegerField()),
                ('issuer', models.CharField(max_length=200)),
                ('underWriter', models.CharField(blank=True, max_length=200, null=True)),
                ('guarantor', models.CharField(max_length=200)),
                ('profitDistributionAgent', models.CharField(max_length=200)),
                ('saleAgent', models.CharField(blank=True, max_length=200, null=True)),
                ('profitDistributionDates', django_mysql.models.ListCharField(models.CharField(max_length=10), max_length=440, size=40)),
                ('profitDistributionValues', django_mysql.models.ListCharField(models.CharField(max_length=12), max_length=520, size=40)),
                ('paymentDetailsDates', django_mysql.models.ListTextField(models.CharField(max_length=11), size=None)),
                ('paymentDetailsValues', django_mysql.models.ListTextField(models.CharField(max_length=14), size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
