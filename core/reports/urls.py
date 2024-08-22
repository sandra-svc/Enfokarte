from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from core.reports.views import ReportSaleView

# Decorador para verificar si el usuario es staff o superusuario
def is_admin_user(user):
    return user.is_staff or user.is_superuser

app_name = 'reports'  # Establecer el namespace

urlpatterns = [
    path('sale/', user_passes_test(is_admin_user)(ReportSaleView.as_view()), name='sale_report'),
]
