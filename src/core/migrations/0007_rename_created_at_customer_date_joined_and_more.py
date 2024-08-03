# Generated by Django 5.0.6 on 2024-08-03 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_customer_is_active_customer_is_staff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='created_at',
            new_name='date_joined',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
