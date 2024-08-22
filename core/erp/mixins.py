# Importa los módulos necesarios
import logging
from datetime import datetime

from crum import get_current_request
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Configura el registro
logger = logging.getLogger(__name__)

class IsSuperuserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return redirect('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_now'] = datetime.now()
        return context


class ValidatePermissionRequiredMixin(object):
    permission_required = ''
    url_redirect = None

    def get_perms(self):
        perms = []
        if isinstance(self.permission_required, str):
            perms.append(self.permission_required)
        else:
            perms = list(self.permission_required)
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('erp:dashboard')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        logger.debug(f"Checking permissions for user {request.user.username} in {self.__class__.__name__}")
        
        if 'group' in request.session:
            group = request.session['group']
            perms = self.get_perms()
            logger.debug(f"User {request.user.username} belongs to group {group}")
            logger.debug(f"Required permissions: {perms}")
            
            for p in perms:
                if not group.permissions.filter(codename=p).exists():
                    logger.warning(f"Permission {p} not granted to user {request.user.username}")
                    messages.error(request, 'No tiene permiso para ingresar a este módulo')
                    return HttpResponseRedirect(self.get_url_redirect())
            
            logger.info(f"User {request.user.username} has necessary permissions. Proceeding with dispatch.")
            return super().dispatch(request, *args, **kwargs)
        
        logger.warning(f"No group found in session for user {request.user.username}")
        messages.error(request, 'No tiene permiso para ingresar a este módulo')
        return HttpResponseRedirect(self.get_url_redirect())

# class ValidatePermissionRequiredMixin(object):
#     permission_required = ''
#     url_redirect = None
#
#     def get_perms(self):
#         if isinstance(self.permission_required, str):
#             perms = (self.permission_required,)
#         else:
#             perms = self.permission_required
#         return perms
#
#     def get_url_redirect(self):
#         if self.url_redirect is None:
#             return reverse_lazy('index')
#         return self.url_redirect
#
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.has_perms(self.get_perms()):
#             return super().dispatch(request, *args, **kwargs)
#         messages.error(request, 'No tiene permiso para ingresar a este módulo')
#         return HttpResponseRedirect(self.get_url_redirect())
