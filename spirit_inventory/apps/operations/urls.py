from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Sell Orders
    path('sell-orders/', views.sell_order_list, name='sell_order_list'),
    path('sell-orders/create/', views.sell_order_form, name='sell_order_create'),
    path('sell-orders/<int:pk>/', views.sell_order_detail, name='sell_order_detail'),
    path('sell-orders/<int:pk>/edit/', views.sell_order_form, name='sell_order_form'),
    path('sell-orders/<int:pk>/delete/', views.sell_order_delete, name='sell_order_delete'),
    path('sell-orders/<int:order_pk>/items/add/<int:product_pk>/', views.sell_item_add, name='sell_item_add'),
    path('sell-orders/<int:order_pk>/items/remove/<int:product_pk>/', views.sell_item_remove, name='sell_item_remove'),
    path('sell-orders/<int:order_pk>/items/bulk-add/', views.sell_items_bulk_add, name='sell_items_bulk_add'),
    path('sell-orders/<int:order_pk>/items/price/', views.sell_item_price_update, name='sell_item_price_update'),
    path('sell-orders/search/', views.sell_order_search, name='sell_order_search'),

    # Return Orders
    path('returns/', views.return_order_list, name='return_order_list'),
    path('returns/create/', views.return_order_form, name='return_order_create'),
    path('returns/<int:pk>/', views.return_order_detail, name='return_order_detail'),
    path('returns/<int:pk>/edit/', views.return_order_form, name='return_order_form'),
    path('returns/<int:pk>/delete/', views.return_order_delete, name='return_order_delete'),
    path('returns/<int:order_pk>/items/add/<int:product_pk>/', views.return_item_add, name='return_item_add'),
    path('returns/<int:order_pk>/items/remove/<int:product_pk>/', views.return_item_remove, name='return_item_remove'),

    # Write-offs
    path('write-offs/', views.write_off_list, name='write_off_list'),
    path('write-offs/select/', views.write_off_select, name='write_off_select'),
    path('write-offs/execute/', views.write_off_execute, name='write_off_execute'),
    path('write-offs/<int:pk>/', views.write_off_detail, name='write_off_detail'),
    path('write-offs/<int:pk>/edit/', views.write_off_update, name='write_off_update'),
    path('write-offs/<int:pk>/delete/', views.write_off_delete, name='write_off_delete'),
]