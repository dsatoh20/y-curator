# Generated by Django 3.0.4 on 2024-03-01 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20240226_0240'),
        ('books', '0005_auto_20240228_0656'),
    ]

    operations = [
        migrations.CreateModel(
            name='Companion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='companion_owner', to='accounts.Account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Account')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='member',
            field=models.ManyToManyField(related_name='member', to='books.Companion'),
        ),
    ]