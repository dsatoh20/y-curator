# Generated by Django 3.0.4 on 2024-02-27 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_bookrecord_isbn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookrecord',
            name='isbn',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
    ]