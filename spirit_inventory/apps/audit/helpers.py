from .models import AuditLog


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, instance, changes=None):
    """
    Record a user action in the audit log.

    Usage in views:
        log_action(request, AuditLog.ACTION_CREATE, sell_order)
        log_action(request, AuditLog.ACTION_UPDATE, product, changes={
            'price': [old_price, new_price]
        })
        log_action(request, AuditLog.ACTION_DELETE, batch)
    """

def get_changes(old_instance, new_instance, fields):
    """
    Compare field values between old and new instance.
    Returns a dict of {field: [old_value, new_value]} for changed fields only.

    Usage:
        old = Product.objects.get(pk=pk)
        form.save()
        new = Product.objects.get(pk=pk)
        changes = get_changes(old, new, ["your firlds here"])
        log_action(request, AuditLog.ACTION_UPDATE, new, changes=changes)
    """
    