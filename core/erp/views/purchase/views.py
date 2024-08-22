import json
import locale
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, View
from weasyprint import HTML, CSS
from .utils import DecimalEncoder



from core.erp.forms import PurchaseForm, SupplierForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Purchase, Product, DetPurchase, Supplier


class PurchaseListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchase/list.html'
    permission_required = 'view_purchase'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Purchase.objects.all()[0:15]:
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetPurchase.objects.filter(purchase_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Compras'
        context['create_url'] = reverse_lazy('erp:purchase_create')
        context['list_url'] = reverse_lazy('erp:purchase_list')
        context['entity'] = 'Compras'
        return context


class PurchaseCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase/create.html'
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'add_purchase'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                products = Product.objects.filter(is_service=False)
                if len(term):
                    products = products.filter(name__icontains=term, is_service=False)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['value'] = i.name
                    # item['text'] = i.name
                    data.append(item)
            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                data.append({'id': term, 'text': term})
                products = Product.objects.filter(name__icontains=term, is_service=False)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['text'] = i.name
                    data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    purchase = Purchase()
                    purchase.date_joined = vents['date_joined']
                    purchase.prov_id = vents['prov']
                    purchase.subtotal = float(vents['subtotal'])
                    purchase.iva = float(vents['iva'])
                    purchase.total = float(vents['total'])
                    purchase.save()
                    for i in vents['products']:
                        det = DetPurchase()
                        det.purchase_id = purchase.id
                        det.prod_id = i['id']
                        det.cant = int(i['cant'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                        product = Product.objects.get(id=i['id'])
                        if  product.is_service == False :
                            det.prod.stock += det.cant
                            det.prod.save()
                    data = {'id': purchase.id}
            elif action == 'search_suppliers':
                data = []
                term = request.POST['term']
                suppliers = Supplier.objects.filter(
                    Q(namessp__icontains=term) | Q(surnamessp__icontains=term) | Q(dnisp__icontains=term))[0:10]
                for i in suppliers:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'create_supplier':
                with transaction.atomic():
                    frmSupplier = SupplierForm(request.POST)
                    data = frmSupplier.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        context['frmSupplier'] = SupplierForm()
        return context


class PurchaseUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase/create.html'
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'change_purchase'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        instance = self.get_object()
        form = PurchaseForm(instance=instance)
        form.fields['prov'].queryset = Supplier.objects.filter(id=instance.prov.id)
        return form

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                products = Product.objects.filter(is_service=False)
                if len(term):
                    products = products.filter(name__icontains=term, is_service=False)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['value'] = i.name
                    # item['text'] = i.name
                    data.append(item)
            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                data.append({'id': term, 'text': term})
                products = Product.objects.filter(name__icontains=term, is_service=False)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['text'] = i.name
                    data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    # Purchase = Purchase.objects.get(pk=self.get_object().id)
                    purchase = self.get_object()
                    purchase.date_joined = vents['date_joined']
                    purchase.prov_id = vents['prov']
                    purchase.subtotal = str(vents['subtotal'])
                    purchase.iva = str(vents['iva'])
                    purchase.total = str(vents['total'])
                    purchase.save()
                    
                                      
                    current_details = {det.prod_id: det for det in purchase.detpurchase_set.all()}
                    print("Detalles de compra actuales:", current_details)

                    for i in vents['products']:
                        det = current_details.get(i['id'])

                        if det:
                            # Si el producto ya existe en el detalle de la venta, actualiza la cantidad
                            old_quantity = det.cant
                            new_quantity = int(i['cant'])
                            det.cant = new_quantity
                            det.price = str(i['pvp'])
                            det.subtotal = str(i['subtotal'])
                            det.save()

                            print(f"Detalle actualizado: Producto {det.prod_id}, Cantidad anterior: {old_quantity}, Nueva cantidad: {new_quantity}")

                            # Verificar si hay una devolución para este producto
                            returned_quantity = old_quantity - new_quantity

                            print(f"Producto: {det.prod.name}, Cantidad devuelta: {returned_quantity}")

                            # Si la cantidad devuelta es mayor que cero, es una devolución
                            if returned_quantity > 0:
                                print(f"Actualizando stock para el producto: {det.prod.name}")
                                det.prod.stock -= returned_quantity
                                det.prod.save()
                                print(f"Nuevo stock: {det.prod.stock}")

                        else:
                            # Si el producto no existe en el detalle de la venta, crea una nueva línea
                            det = DetPurchase()
                            det.purchase_id = purchase.id
                            det.prod_id = i['id']
                            det.cant = int(i['cant'])
                            det.price = str(i['pvp'])
                            det.subtotal = str(i['subtotal'])
                            det.save()

                            print(f"Detalle agregado: Producto {det.prod_id}, Cantidad: {det.cant}")

                    data = {'id': purchase.id}

            elif action == 'search_suppliers':
                data = []
                term = request.POST['term']
                suppliers = Supplier.objects.filter(
                    Q(namessp__icontains=term) | Q(surnamessp__icontains=term) | Q(dnisp__icontains=term))[0:10]
                for i in suppliers:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'create_supplier':
                with transaction.atomic():
                    frmSupplier = SupplierForm(request.POST)
                    data = frmSupplier.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data = []
        try:
            for i in DetPurchase.objects.filter(purchase_id=self.get_object().id):
                item = i.prod.toJSON()
                item['cant'] = i.cant
                data.append(item)
        except:
            pass
        return data

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_details_product(),cls=DecimalEncoder)
        context['frmSupplier'] = SupplierForm()
        return context


class PurchaseDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'purchase/delete.html'
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'delete_purchase'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        return context


class PurchaseInvoicePdfView(View):

    def get(self, request, *args, **kwargs):
        try:
                      
             locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Configurar localización

             template = get_template('purchase/invoice.html')
             context = {
                'Purchase': Purchase.objects.get(pk=self.kwargs['pk']),
            }
            
            
            # Formatear el campo total con separadores de miles y dos decimales
             
             context['Purchase'].subtotal = locale.format_string("%.2f", context['Purchase'].subtotal, grouping=True)
             context['Purchase'].iva = locale.format_string("%.2f", context['Purchase'].iva, grouping=True)
             context['Purchase'].total = locale.format_string("%.2f", context['Purchase'].total, grouping=True)

             html = template.render(context)
             css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
             pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
             return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('erp:purchase_list'))