# Generated by Django 5.0.1 on 2024-06-24 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0023_productphase'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='productphase',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productphase',
            name='phase',
            field=models.CharField(choices=[('Alistamiento', 'Alistamiento'), ('Seleccion', 'Selección'), ('Proceso', 'Proceso'), ('Revisión', 'Revisión'), ('Terminado', 'Terminado'), ('Entregado', 'Entregado')], max_length=50),
        ),
        migrations.AlterField(
            model_name='productphase',
            name='status',
            field=models.CharField(max_length=100),
        ),
    ]
