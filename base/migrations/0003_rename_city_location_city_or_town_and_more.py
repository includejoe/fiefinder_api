# Generated by Django 4.2.8 on 2023-12-25 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_country_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='city',
            new_name='city_or_town',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='region',
            new_name='region_or_state',
        ),
        migrations.RemoveField(
            model_name='location',
            name='name',
        ),
    ]
