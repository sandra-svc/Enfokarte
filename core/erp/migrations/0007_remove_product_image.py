# Generated by Django 5.0.1 on 2024-04-11 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0006_remove_client_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
