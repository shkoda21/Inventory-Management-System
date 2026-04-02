from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

from .models import AuditLog
from apps.accounts.permissions import supervisor_required


@login_required
@supervisor_required
def log_list(request):
    qs = AuditLog.objects.select_related('user').order_by('-timestamp')

    # Get search query
    #filteing logic

    page_obj = Paginator(qs, 50).get_page(request.GET.get('page'))
    models   = AuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')

    return render(request, 'audit/log_list.html', {"context": context})
        