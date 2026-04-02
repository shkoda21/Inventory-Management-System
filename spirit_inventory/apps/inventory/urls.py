from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('capacities/', views.capacity_list, name='capacity_list'),
    path('capacities/save/', views.capacity_save, name='capacity_create'),
    path('capacities/<int:pk>/save/', views.capacity_save, name='capacity_update'),
    path('capacities/<int:pk>/delete/', views.capacity_delete, name='capacity_delete'),
    path('types/', views.type_list, name='type_list'),
    path('types/save/', views.type_save, name='type_create'),
    path('types/<int:pk>/save/', views.type_save, name='type_update'),
    path('types/<int:pk>/delete/', views.type_delete, name='type_delete'),
    path('barcodes/', views.barcode_list, name='barcode_list'),
    path('barcodes/save/', views.barcode_save, name='barcode_create'),
    path('barcodes/<int:pk>/save/', views.barcode_save, name='barcode_update'),
    path('barcodes/<int:pk>/delete/', views.barcode_delete, name='barcode_delete'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batches/<int:pk>/edit/', views.batch_update, name='batch_update'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
    path('batches/<int:batch_pk>/ingredients/add/', views.ingredient_add, name='ingredient_add'),
    path('ingredients/update/', views.ingredient_update, name='ingredient_update'),
    path('ingredients/delete/', views.ingredient_delete, name='ingredient_delete'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('retailers/', views.retailer_list, name='retailer_list'),
    path('retailers/create/', views.retailer_create, name='retailer_create'),
    path('retailers/<int:pk>/', views.retailer_detail, name='retailer_detail'),
    path('retailers/<int:pk>/edit/', views.retailer_update, name='retailer_update'),
    path('retailers/<int:pk>/delete/', views.retailer_delete, name='retailer_delete'),
    path('retailers/autocomplete/', views.retailer_autocomplete, name='retailer_autocomplete'),
]