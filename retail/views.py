from django.shortcuts import render
from inventory.models import Supplier, Product, Restock,Sale
from django.db.models import Sum, F, Count, Avg
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def home_view(request):
    return render(request, 'base.html')

def dashboard_view(request):
    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum(F('quantity_sold') * F('sale_price')))['total'] or 0
    low_stock = Product.objects.filter(quantity__lt=10).count()

    top_brand = Sale.objects.values('product__brand__name') \
        .annotate(total_sales=Sum(F('quantity_sold') * F('sale_price'))) \
        .order_by('-total_sales').first()
    
    if top_brand:
        top_brand_name = top_brand['product__brand__name']
    else:
        top_brand_name = "N/A" 

    recent_sales = Sale.objects.select_related('product').order_by('-sale_date')[:5]

    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'low_stock': low_stock,
        'top_brand': top_brand_name, 
        'recent_sales': recent_sales,
    }

    return render(request, 'dashboard.html', context)
