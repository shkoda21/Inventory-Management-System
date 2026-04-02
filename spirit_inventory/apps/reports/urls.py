from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('ttb/', views.ttb_report, name='ttb_report'),
    path('ttb/export/', views.ttb_export, name='ttb_export'),
    path('ttb/export-by-retailer/', views.ttb_export_by_retailer, name='ttb_export_by_retailer'),
    path('ttb/export-attached/', views.ttb_export_attached_table, name='ttb_export_attached'),
    path('analysis/', views.analysis, name='analysis'),
]