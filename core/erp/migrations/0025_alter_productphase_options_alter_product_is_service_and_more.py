# Generated by Django 5.0.1 on 2024-07-08 23:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0024_productphase_user_alter_productphase_phase_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productphase',
            options={'ordering': ['id'], 'permissions': [('view_phase', 'Can view phase')], 'verbose_name': 'Fase de Producto', 'verbose_name_plural': 'Fases de Productos'},
        ),
        migrations.AlterField(
            model_name='product',
            name='is_service',
            field=models.BooleanField(default=False, verbose_name='Es servicio?'),
        ),
        migrations.AlterField(
            model_name='productphase',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
