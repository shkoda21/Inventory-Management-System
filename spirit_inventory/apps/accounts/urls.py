from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',           views.login_view,          name='login'),
    # Add other account-related URLs here, e.g. logout, profile, user management, etc.
]