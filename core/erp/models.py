from datetime import datetime
import locale

from django.db import models
from django.forms import model_to_dict

from django.db.models import Sum
from django.db.models.functions import Coalesce


from config.settings import MEDIA_URL, STATIC_URL
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model






class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['id']


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    stock = models.IntegerField(default=0, verbose_name='Stock')
    is_service = models.BooleanField (default=False, verbose_name='Es servicio?')
    pvp = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Precio de venta')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValidationError("No tiene stock suficiente.El stock no puede ser negativo")
        super().save(*args, **kwargs) 
        
    def toJSON(self):
        item = model_to_dict(self)
        item['full_name'] = '{}  {}'.format(self.name, self.cat.name)
        item['cat'] = self.cat.toJSON()
        item['stock'] = self.stock
        item['is_service'] = self.is_service
        item['pvp'] = str(self.pvp)
        return item

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['id']


class Client(models.Model):
    dni = models.CharField(max_length=10, unique=True, verbose_name='Dni')
    names = models.CharField(max_length=150, verbose_name='Nombres')
    surnames = models.CharField(max_length=150, verbose_name='Apellidos')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dirección')
    email = models.EmailField(max_length=255, verbose_name='Email', null=True, blank=True)  
    phone_number = models.CharField(max_length=15, verbose_name='Teléfono', null=True, blank=True)  
    
    
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '{} {}  {}'.format(self.dni,self.names, self.surnames)

    def toJSON(self):
     return {
        'id': self.id,
        'dni': self.dni,
        'names': self.names,
        'surnames': self.surnames,
        'address': self.address,
        'email': self.email,
        'phone_number': self.phone_number,
        
    }

    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']


class Sale(models.Model):
    
    cli = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    date_end = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    iva = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
        

    def __str__(self):
        return self.cli.names

    def saldo_pendiente(self):
        total_pagos = self.payment_set.aggregate(total_pagos=Sum('amount'))['total_pagos'] or 0
        saldo = self.total - total_pagos
        print("Saldo pendiente:", saldo)
        return saldo
    
    def total_pago(self):
        total_pago = self.payment_set.aggregate(total_pagos=models.Sum('amount'))['total_pagos'] or 0
        return locale.currency(total_pago, grouping=True, symbol=False)

    def toJSON(self):
        item = model_to_dict(self)
        item['cli'] = self.cli.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['date_end'] = self.date_end.strftime('%Y-%m-%d')
        item['total'] =format(self.total, '.2f')
        item['det'] = [i.toJSON() for i in self.detsale_set.all()]
        return item

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']


class DetSale(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cambia a DecimalField
    cant = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cambia a DecimalField


    def __str__(self):
        return self.prod.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['prod'] = self.prod.toJSON()
        item['price'] = str(self.price)
        item['subtotal'] = str(self.subtotal)
        item['phases'] = [phase.phase for phase in self.phases.all()]
        return item

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        ordering = ['id']

class Supplier(models.Model):
    dnisp = models.CharField(max_length=10, unique=True, verbose_name='Dni')
    namessp = models.CharField(max_length=150, verbose_name='Nombres')
    surnamessp = models.CharField(max_length=150, verbose_name='Apellidos')
    addresssp = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dirección')
    emailsp = models.EmailField(max_length=255, verbose_name='Email', null=True, blank=True)  
    phone_numbersp = models.CharField(max_length=15, verbose_name='Teléfono', null=True, blank=True)  
    
    
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '{} {}  {}'.format(self.dnisp,self.namessp, self.surnamessp)

    def toJSON(self):
     return {
        'id': self.id,
        'dnisp': self.dnisp,
        'namessp': self.namessp,
        'surnamessp': self.surnamessp,
        'addresssp': self.addresssp,
        'emailsp': self.emailsp,
        'phone_numbersp': self.phone_numbersp,
        
    }

    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['id']
        
class Purchase(models.Model):
    prov = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    iva = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return self.prov.namessp
    
    
    def toJSON(self):
        item = model_to_dict(self)
        item['prov'] = self.prov.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['det'] = [i.toJSON() for i in self.detpurchase_set.all()]
        return item

    def delete(self, using=None, keep_parents=False):
        for det in self.detpurchase_set.all():
             product = det.prod
             if product.is_service:  # Verificar si es un servicio
                continue  # Pasar al siguiente detalle si es un servicio
             product.stock -= det.cant
             product.save()
        super(Purchase, self).delete()

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['id']


class DetPurchase(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cambia a DecimalField
    cant = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cambia a DecimalField


    def __str__(self):
        return self.prod.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['prod'] = self.prod.toJSON()
        item['price'] = str(self.price)
        item['subtotal'] = str(self.subtotal)
        return item

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalle de Compras'
        ordering = ['id']


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('EF', 'Efectivo'),
        ('NQ', 'Nequi'), 
        ('QR', 'QR'),
        # Agrega más opciones según sea necesario
    )
    PAYMENT_FORM_CHOICES = (
        ('CNT', 'Contado'),
        ('CRD', 'Credito'),
        # Agrega más opciones según sea necesario
    )

    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    payment_date = models.DateField(default=datetime.now)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_form = models.CharField(max_length=3, choices=PAYMENT_FORM_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Payment for Sale {self.sale}, Amount: {self.amount}, Date: {self.payment_date}"
        
    def toJSON(self):
        item = model_to_dict(self)
        sale_data = model_to_dict(self.sale)
        item['sale'] = sale_data  # Suponiendo que la relación sale existe y también tiene un método toJSON
        item['amount'] = format(self.amount, '.2f')
        item['payment_date'] = self.payment_date.strftime('%Y-%m-%d')
        item['payment_method'] = self.payment_method
        item['payment_form']= self.payment_form
        return item

class ProductPhase(models.Model):
    
        
    PHASE_CHOICES = [
        ('Alistamiento', 'Alistamiento'),
        ('Seleccion', 'Selección'),
        ('Proceso', 'Proceso'),
        ('Revisión', 'Revisión'),
        ('Terminado', 'Terminado'),
        ('Entregado', 'Entregado'),
    ]

    det_sale = models.ForeignKey(DetSale, on_delete=models.CASCADE, related_name='phases')
    phase = models.CharField(max_length=50, choices=PHASE_CHOICES)
    date = models.DateField()
    status = models.CharField(max_length=100)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE) 

    def __str__(self):
        return f'{self.det_sale.prod.name} - {self.phase}'
    
    @classmethod
    def get_last_phase(cls, det_sale_id):
        phases = cls.objects.filter(det_sale_id=det_sale_id).order_by('-date')
        return phases.first() if phases.exists() else None

    def toJSON(self):
        item = model_to_dict(self)
        item['det_sale'] = self.det_sale.toJSON()
        item['phase'] = self.phase
        item['date'] = self.date.strftime('%Y-%m-%d')
        item['status'] = self.status
        item['user'] = self.user.get_full_name() if self.user else ''   # Add user information        
        return item

    class Meta:
        verbose_name = 'Fase de Producto'
        verbose_name_plural = 'Fases de Productos'
        ordering = ['id']
        permissions = [
            ('view_phase', 'Can view phase'),
        ]    
   