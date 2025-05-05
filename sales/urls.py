from django.urls import path
from . import views

urlpatterns = [
    path('sales-history/', views.sales_history_view, name='sales_history'),
    path('sales/', views.sales_view, name='sales'),
    path('sales-receipt/', views.sales_receipt, name='sales_receipt'),
]