# Generated by Django 3.0.4 on 2024-02-27 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_chat_reply_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookrecord',
            name='isbn',
            field=models.TextField(blank=True, max_length=17, null=True),
        ),
    ]