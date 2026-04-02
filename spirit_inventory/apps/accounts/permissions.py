from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
 
 
class RoleRequiredMixin(LoginRequiredMixin):
    """
    Base mixin. Subclass and set `required_permission` to a string
    matching a User property, e.g. 'can_write', 'can_delete_operations'.
    """
    required_permission = None
 
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_permission:
            if not getattr(request.user, self.required_permission, False):
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
 
 
# --- Ready-made mixins for common gates -----------------------------------
 
class WriteRequiredMixin(RoleRequiredMixin):
    required_permission = 'can_write'
 
    # add your other mixins here, e.g. AdminRequiredMixin, etc.
 
# --- Function-based view decorators ---------------------------------------
 
def role_required(permission):
    """
    Decorator for function-based views.
    Usage: @role_required('can_write')
    """
    def decorator(view_func):
        return decorator
 
    #Add your decorator implementation here, similar to the mixin logic, checking request.user and permission.