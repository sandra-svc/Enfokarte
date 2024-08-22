# Generated by Django 5.0.1 on 2024-04-21 21:56

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0014_purchase_detpurchase'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del método de pago')),
            ],
            options={
                'verbose_name': 'Método de Pago',
                'verbose_name_plural': 'Métodos de Pago',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Monto del pago')),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Fecha y hora del pago')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='erp.sale', verbose_name='Venta relacionada')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.paymentmethod', verbose_name='Método de pago')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
            },
        ),
    ]
