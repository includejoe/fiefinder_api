# Generated by Django 4.2.8 on 2023-12-28 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_token_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='expiry_date',
        ),
    ]
