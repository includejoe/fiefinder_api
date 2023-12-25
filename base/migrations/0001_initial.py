# Generated by Django 4.2.8 on 2023-12-24 19:09

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('short_name', models.CharField(blank=True, max_length=5, null=True)),
                ('phone_code', models.CharField(blank=True, max_length=5, null=True)),
                ('currency', models.CharField(blank=True, max_length=120, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=5, null=True)),
                ('image', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='PushToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(blank=True, max_length=256, null=True)),
                ('device', models.CharField(blank=True, max_length=450, null=True)),
                ('os', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('message', models.TextField()),
                ('general', models.BooleanField(default=False)),
                ('recipients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opened_by', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('region', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(blank=True, max_length=128, null=True)),
                ('street', models.CharField(blank=True, max_length=128, null=True)),
                ('landmark', models.CharField(blank=True, max_length=128, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='base.country')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('short_code', models.CharField(blank=True, max_length=5, null=True)),
                ('image', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-name'],
                'indexes': [models.Index(fields=['name', 'short_code'], name='base_langua_name_21b5fb_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='country',
            index=models.Index(fields=['name'], name='base_countr_name_0d4498_idx'),
        ),
        migrations.AddIndex(
            model_name='pushtoken',
            index=models.Index(fields=['fcm_token'], name='base_pushto_fcm_tok_5dc5fc_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['title', 'message'], name='base_notifi_title_4994ed_idx'),
        ),
    ]