# Generated by Django 3.0.4 on 2024-05-17 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articlechat',
            old_name='articlerecord',
            new_name='record',
        ),
    ]