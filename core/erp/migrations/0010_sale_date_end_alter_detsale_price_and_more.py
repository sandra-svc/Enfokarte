# Generated by Django 5.0.1 on 2024-04-15 13:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0009_remove_product_is_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='date_end',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='detsale',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='detsale',
            name='subtotal',
            field=models.IntegerField(default=0),
        ),
    ]
