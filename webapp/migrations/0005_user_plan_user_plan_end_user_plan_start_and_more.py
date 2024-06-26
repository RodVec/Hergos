# Generated by Django 5.0.2 on 2024-06-11 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_user_email_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='plan',
            field=models.CharField(default='Ninguno', max_length=15),
        ),
        migrations.AddField(
            model_name='user',
            name='plan_end',
            field=models.DateField(default='2100-12-31'),
        ),
        migrations.AddField(
            model_name='user',
            name='plan_start',
            field=models.DateField(default='2100-12-31'),
        ),
        migrations.AddField(
            model_name='user',
            name='plan_status',
            field=models.CharField(default='Inactivo', max_length=15),
        ),
    ]
