# Generated by Django 3.0.4 on 2024-04-02 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_auto_20240328_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='comment',
            field=models.TextField(max_length=500),
        ),
    ]
