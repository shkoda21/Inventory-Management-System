from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('generate/<int:order_pk>/', views.generate_from_order, name='generate_from_order'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('<int:pk>/export/', views.invoice_export_docx, name='invoice_export_docx'),
    path('<int:invoice_pk>/payments/add/', views.payment_add, name='payment_add'),
    path('payments/<int:payment_pk>/delete/', views.payment_delete, name='payment_delete'),
]