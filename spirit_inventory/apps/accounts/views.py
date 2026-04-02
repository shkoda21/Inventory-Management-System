from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import User
from .forms import LoginForm, UserCreateForm, UserUpdateForm, ProfileUpdateForm
from .permissions import admin_required
from apps.audit.helpers import log_action
from apps.audit.models import AuditLog


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'inventory:dashboard'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')
    return render(request, 'accounts/logout_confirm.html')

"""Add views for user registration, profile management, password change, and admin user management below.
@login_required
def profile_view(request)

@login_required
def password_change_view(request)

@login_required
@admin_required
def user_list(request)


@login_required
@admin_required
def user_create(request)

@login_required
@admin_required
def user_update(request, pk)
"""


