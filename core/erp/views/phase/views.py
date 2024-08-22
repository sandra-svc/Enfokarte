from argparse import Action
from audioop import reverse
from decimal import Decimal
import json
import locale
from pyexpat.errors import messages
from babel.numbers import format_currency
import os
import pdb
from urllib import request

from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML, CSS
from django.db.models import OuterRef, Subquery, Max

from core.erp.forms import ProductPhaseForm, SaleForm, ClientForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Sale, DetSale, ProductPhase

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(permission_required('erp.view_phase', login_url='/login/', raise_exception=True), name='dispatch')
class PhaseListView(LoginRequiredMixin, ListView):
    model = ProductPhase
    template_name = 'phase/list.html'
    context_object_name = 'phases'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        print(f"User: {user.username}")  # Mensaje de depuración
        user_groups = user.groups.all()
        for group in user_groups:
            print(f"Group: {group.name}")  # Mensaje de depuración

        return super().dispatch(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            user = request.user  # Obtener el usuario logueado
            is_admin = user.is_superuser  # Verificar si el usuario es administrador

            if action == 'searchdata':
                data = []
                sales = Sale.objects.all()  # Puedes ajustar el rango de resultados si es necesario

                for sale in sales:
                    sale_data = sale.toJSON()
                    sale_details = []

                    for det in sale_data['det']:
                        last_phase = ProductPhase.get_last_phase(det['id'])
                        
                        if last_phase and last_phase.phase == 'Entregado':
                           continue
                        

                        if is_admin or (last_phase and last_phase.user == user):
                            last_phase_info = {
                                'phase': last_phase.phase if last_phase else 'No phase',
                                'status': last_phase.status if last_phase else 'No status',
                                'user': last_phase.user.get_full_name() if last_phase and last_phase.user else 'Sin asignar',
                            }
                            det.update(last_phase_info)
                            sale_details.append(det)

                    if sale_details:  # Solo agregar ventas que tienen detalles filtrados
                        sale_data['det'] = sale_details
                        data.append(sale_data)

                print(f'Final data: {data}')  # Imprime los datos finales
                return JsonResponse(data, safe=False)

            elif action == 'search_details_prod':
                sale_id = request.POST.get('id')
                print(f'Received sale_id: {sale_id}')  # Imprime el ID de la venta recibido
                details = DetSale.objects.filter(sale_id=sale_id)
                data = []

                for det in details:
                    last_phase = ProductPhase.get_last_phase(det.id)

                    if is_admin or (last_phase and last_phase.user == user):
                        data.append({
                            'date': last_phase.date.strftime('%Y-%m-%d') if last_phase else '',
                            'phase': last_phase.phase if last_phase else '',
                            'status': last_phase.status if last_phase else '',
                            'user': last_phase.user.get_full_name() if last_phase and last_phase.user else '',
                        })

                return JsonResponse(data, safe=False)

        except Exception as e:
            import traceback
            traceback.print_exc()
            data['error'] = str(e)
            return JsonResponse(data, status=500)

        return JsonResponse(data, safe=False)


    
class UpdatePhaseView(LoginRequiredMixin, TemplateView):
    model = ProductPhase
    template_name = 'phase/create.html'
    permission_required = 'view_phase'

    def post(self, request, *args, **kwargs):
        sale_id = self.kwargs['sale_id']
        product_id = self.kwargs['product_id']
        sale = get_object_or_404(Sale, id=sale_id)
        det_sale = get_object_or_404(DetSale, id=product_id, sale=sale)
        form = ProductPhaseForm(request.POST)
        if form.is_valid():
            phase = form.save(commit=False)
            phase.det_sale = det_sale
            phase.save()
            response_data = {
                'status': 'success',
                'phase': {
                    'date': phase.date.strftime('%Y-%m-%d'),
                    'phase': phase.phase,
                    'status': phase.status,
                    'user':  phase.user.get_full_name() if phase.user else '',  # Asegúrate de obtener el nombre completo del usuario
                    'product_id': phase.det_sale.id,
                    'product_name': phase.det_sale.prod.name,
                    'quantity': phase.det_sale.cant,
                }
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_id = self.kwargs['sale_id']
        product_id = self.kwargs['product_id']
        sale = get_object_or_404(Sale, id=sale_id)
        det_sale = get_object_or_404(DetSale, id=product_id, sale=sale)
        context['sale'] = sale
        context['det_sale'] = det_sale
        context['form'] = ProductPhaseForm()
        return context






