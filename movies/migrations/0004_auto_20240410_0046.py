# Generated by Django 3.0.4 on 2024-04-09 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_auto_20240403_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movierecord',
            name='summary',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
