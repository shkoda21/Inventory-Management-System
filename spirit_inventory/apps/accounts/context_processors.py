def user_role(request):
    """
    Exposes role permission flags to every template.
    Usage in template: {% if can_write %}...{% endif %}
    """
    if not request.user.is_authenticated:
        return {}
    user = request.user
    return {
        'can_write':                 user.can_write,
        'can_export':                user.can_export,
        'can_delete_operations':     user.can_delete_operations,
        'can_delete_reference_data': user.can_delete_reference_data,
        'can_manage_users':          user.can_manage_users,
        'can_view_expenses':         user.can_view_expenses,
        'can_view_audit_log':        user.can_view_audit_log,
        'can_view_ttb':              user.can_view_ttb,
        'can_export_ttb':            user.can_export_ttb,
        'user_role':                 user.role,
        'is_admin':                  user.is_admin,
        'is_supervisor':             user.is_supervisor,
        'is_manager':                user.is_manager,
    }