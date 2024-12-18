# Generated by Django 3.0.4 on 2024-03-28 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_bookrecord_img_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookrecord',
            name='first_author',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='bookrecord',
            name='summary',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
