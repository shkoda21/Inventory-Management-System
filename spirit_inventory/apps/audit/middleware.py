from .models import AuditLog
from .helpers import get_client_ip


class AuditMiddleware:
    """
    Automatically logs login and logout events.
    All other actions are logged explicitly in views via log_action().
    """

# Signal-based login/logout tracking (registered in apps.py)
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_LOGIN,
        model_name='User',
        object_id=user.pk,
        object_repr=str(user),
        ip_address=get_client_ip(request),
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.ACTION_LOGOUT,
            model_name='User',
            object_id=user.pk,
            object_repr=str(user),
            ip_address=get_client_ip(request),
        )