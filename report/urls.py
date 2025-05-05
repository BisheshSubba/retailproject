from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sales_reports, name='sales_reports'),
    path('inventory/', views.inventory_reports, name='inventory_reports'),
    path('restock/<int:product_id>/', views.restock_product, name='restock_product'),
    path('financial/', views.financial_reports, name='financial_reports'),
    path('supplier/', views.supplier_reports, name='supplier_reports'),
]