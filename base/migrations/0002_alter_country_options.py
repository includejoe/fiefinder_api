# Generated by Django 4.2.8 on 2023-12-24 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['-name'], 'verbose_name_plural': 'Countries'},
        ),
    ]
