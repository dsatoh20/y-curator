# Generated by Django 3.0.4 on 2024-02-25 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_image',
            field=models.ImageField(blank=True, upload_to='profile_pics'),
        ),
    ]