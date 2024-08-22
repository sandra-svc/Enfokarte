import decimal
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.erp.models import Sale
from django.contrib.auth.decorators import user_passes_test


class ReportSaleView(TemplateView):
    template_name = 'sale/report.html'
    

    @method_decorator(csrf_exempt)
    @method_decorator(user_passes_test(lambda u: u.is_staff or u.is_superuser))  # type: ignore # Decorador para verificar si es staff o superusuario
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                search = Sale.objects.all()
                if start_date and end_date:
                    search = search.filter(date_joined__range=[start_date, end_date])

                report_data = []
                total_ventas_general = decimal.Decimal(0.0)
                abonos_total_general = decimal.Decimal(0.0)
                subtotal_por_pago = {}

                for s in search:
                    abonos_total = decimal.Decimal(0.0)
                    formas_pago = {}
                    for payment in s.payment_set.all():
                        abono = decimal.Decimal(payment.amount)
                        abonos_total += abono
                        forma_pago = payment.payment_method if payment.payment_method else 'N/A'
                        if forma_pago not in formas_pago:
                            formas_pago[forma_pago] = decimal.Decimal(0.0)
                        formas_pago[forma_pago] += abono

                    formas_pago_str = ', '.join([f"{forma}: {format(amount, ',.2f')}" for forma, amount in formas_pago.items()])
                    abonos_str = '; '.join([f"{forma}={format(amount, ',.2f')}" for forma, amount in formas_pago.items()])

                    report_data.append([
                        s.id,
                        '{} {}'.format(s.cli.names, s.cli.surnames), 
                        s.date_joined.strftime('%Y-%m-%d'),
                        format(decimal.Decimal(s.total), ',.2f'),  # Formatear total como número decimal con coma
                        abonos_str,  # Mostrar tipos de abono y cantidades
                        format(decimal.Decimal(s.total - abonos_total), ',.2f'),  # Formatear saldo como número decimal con coma
                    ])

                    total_ventas_general += s.total
                    abonos_total_general += abonos_total

                    # Agregar subtotales por forma de pago al reporte
                    for forma_pago, subtotal in formas_pago.items():
                        if forma_pago not in subtotal_por_pago:
                            subtotal_por_pago[forma_pago] = decimal.Decimal(0.0)
                        subtotal_por_pago[forma_pago] += subtotal

                # Agregar subtotales por tipo de pago al final del reporte
                for forma_pago, subtotal in subtotal_por_pago.items():
                    report_data.append([
                        '',
                        '',
                        '',
                        f'Subtotal {forma_pago}',
                        format(subtotal, ',.2f'),  # Formatear subtotal como número decimal con coma
                        '',
                    ])

                # Añadir total general al final del reporte
                report_data.append([
                    '',
                    '',
                    'Total General',
                    format(total_ventas_general, ',.2f'),  # Formatear total general como número decimal con coma
                    format(abonos_total_general, ',.2f'),  # Formatear abonos totales como número decimal con coma
                    format(total_ventas_general - abonos_total_general, ',.2f'),  # Formatear saldo total como número decimal con coma
                ])

                data['report_data'] = report_data

            else:
                data['error'] = 'Acción no válida'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)




































