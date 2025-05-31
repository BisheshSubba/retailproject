from django.shortcuts import render
from inventory.models import Supplier, Product, Restock, Sale
from django.db.models import Sum, F, Count, Avg
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth, TruncDay, TruncYear


def home_view(request):
    return render(request, 'base.html')

def sales_data(request, period):
    today = datetime.today()
    
    if period == 'day':
        start_date = today - timedelta(days=30)
        sales = Sale.objects.filter(sale_date__gte=start_date) \
                   .annotate(date=TruncDay('sale_date')) \
                   .values('date') \
                   .annotate(total_sales=Sum(F('quantity_sold') * F('sale_price'))) \
                   .order_by('date')
    elif period == 'month':
        start_date = today - timedelta(days=365)
        sales = Sale.objects.filter(sale_date__gte=start_date) \
                   .annotate(date=TruncMonth('sale_date')) \
                   .values('date') \
                   .annotate(total_sales=Sum(F('quantity_sold') * F('sale_price'))) \
                   .order_by('date')
    else:  # year
        sales = Sale.objects.annotate(date=TruncYear('sale_date')) \
                   .values('date') \
                   .annotate(total_sales=Sum(F('quantity_sold') * F('sale_price'))) \
                   .order_by('date')

    # Format dates properly for JSON serialization
    formatted_sales = []
    for sale in sales:
        formatted_sales.append({
            'sale_date': sale['date'].strftime('%Y-%m-%d'),
            'total_sales': float(sale['total_sales']) if sale['total_sales'] else 0.0
        })
    
    return JsonResponse(formatted_sales, safe=False)


def dashboard_view(request):
    # Basic metrics
    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum(F('quantity_sold') * F('sale_price')))['total'] or 0
    low_stock = Product.objects.filter(quantity__lt=10).count()

    # Top brand by sales
    top_brand = Sale.objects.values('product__brand__name') \
                  .annotate(total_sales=Sum(F('quantity_sold') * F('sale_price'))) \
                  .order_by('-total_sales') \
                  .first()
    
    top_brand_name = top_brand['product__brand__name'] if top_brand else "N/A"

    # Recent sales (last 5)
    recent_sales = Sale.objects.select_related('product') \
                      .order_by('-sale_date')[:5]

    # Get top 3 products by revenue with product data
    top_shoes = Sale.objects.select_related('product') \
                .values(
                    'product__id',
                    'product__name',
                    'product__brand__name',
                    'product__image'  # Access the product's image field
                ).annotate(
                    total_sales=Sum('quantity_sold'),
                    total_revenue=Sum(F('quantity_sold') * F('sale_price'))
                ).order_by('-total_revenue')[:3]

    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'low_stock': low_stock,
        'top_brand': top_brand_name,
        'recent_sales': recent_sales,
        'top_shoes': top_shoes,
    }
    return render(request, 'dashboard.html', context)