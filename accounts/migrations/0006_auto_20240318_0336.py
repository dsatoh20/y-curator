# Generated by Django 3.0.4 on 2024-03-17 18:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20240318_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='secret_key',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(8)]),
        ),
    ]
