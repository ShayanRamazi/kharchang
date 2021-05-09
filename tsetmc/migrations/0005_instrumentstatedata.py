# Generated by Django 3.0.5 on 2021-04-25 14:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tsetmc', '0004_auto_20210424_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstrumentStateData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField()),
                ('instrumentId', models.CharField(max_length=30)),
                ('time', models.TimeField()),
                ('status', models.CharField(choices=[('I', 'ممنوع'), ('A', 'مجاز'), ('AG', 'مجاز-مسدود'), ('AS', 'مجاز-متوقف'), ('AR', 'مجاز-محفوظ'), ('IG', 'ممنوع-مسدود'), ('IS', 'ممنوع-متوقف'), ('IR', 'ممنوع-محفوظ')], max_length=2)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]