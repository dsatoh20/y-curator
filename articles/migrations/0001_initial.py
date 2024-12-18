# Generated by Django 3.0.4 on 2024-04-22 04:39

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0011_auto_20240401_2221'),
        ('books', '0010_auto_20240410_0046'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField(blank=True, max_length=100, null=True)),
                ('title', models.TextField(max_length=100)),
                ('first_author', models.TextField(max_length=100)),
                ('pub_year', models.DateField()),
                ('genre', models.TextField(max_length=100)),
                ('genre_img', models.TextField(blank=True, null=True)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('summary', models.TextField(max_length=1000)),
                ('report', models.TextField(max_length=5000)),
                ('good_count', models.IntegerField(default=0)),
                ('chat_count', models.IntegerField(default=0)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('edit_date', models.DateTimeField(auto_now=True)),
                ('edit_count', models.IntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Group')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_owner', to='accounts.Account')),
            ],
            options={
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='ArticleChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=500)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('reply_id', models.IntegerField(default=-1)),
                ('reply_count', models.IntegerField(default=0)),
                ('articlerecord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.ArticleRecord')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articlechat_owner', to='accounts.Account')),
            ],
            options={
                'ordering': ('pub_date',),
            },
        ),
    ]
