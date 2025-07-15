from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Count, Avg, Value
from django.utils import timezone
from datetime import timedelta
from django.db.models import (
    Sum, Count, Avg, Max, F, FloatField,
    ExpressionWrapper, Subquery, OuterRef, StdDev
)
from django.http import JsonResponse
from django.db.models.functions import Coalesce
from django.contrib import messages
from inventory.models import Product, Sale, Restock, Supplier, Brand, ProductReturn

def sales_reports(request):

    time_period = request.GET.get('period', 'month') 

    now = timezone.now()
    if time_period == 'week':
        start_date = now - timedelta(days=7)
    elif time_period == 'month':
        start_date = now - timedelta(days=30)
    else:  
        start_date = now - timedelta(days=365)
   
    sales_data = Sale.objects.filter(
        sale_date__gte=start_date
    ).values(
        'product__name', 'product__brand__name'
    ).annotate(
        total_sold=Sum('quantity_sold'),
        total_revenue=Sum(F('quantity_sold') * F('sale_price'))
    ).order_by('-total_revenue')
    
    context = {
        'sales_data': sales_data,
        'time_period': time_period,
    }
    return render(request, 'report/sales_reports.html', context)

def compare_products(request):
    try:
        product1_id = request.GET.get('product1')
        product2_id = request.GET.get('product2')
        
        if not product1_id or not product2_id:
            return JsonResponse({'error': 'Both product IDs are required'}, status=400)
        
        # Get time periods for stock movement chart (last 30 days)
        time_periods = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, -1, -1)]
        
        # Get data for product 1
        product1 = get_object_or_404(Product, id=product1_id)
        product1_data = get_product_comparison_data(product1, time_periods)
        
        # Get data for product 2
        product2 = get_object_or_404(Product, id=product2_id)
        product2_data = get_product_comparison_data(product2, time_periods)
        
        response_data = {
            'product1': product1_data,
            'product2': product2_data,
            'time_periods': time_periods,
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_comparison_data(product, time_periods):
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Get actual sales data with correct Coalesce usage
    sales_data = Sale.objects.filter(
        product=product,
        sale_date__gte=thirty_days_ago
    ).aggregate(
        total_sales=Coalesce(Sum('quantity_sold'), Value(0)),
        total_revenue=Coalesce(
            Sum(ExpressionWrapper(F('quantity_sold') * F('sale_price'), output_field=FloatField())),
            Value(0.0)
        ),
        sales_count=Count('id')
    )
    
    # Calculate sales velocity (units per day)
    sales_velocity = sales_data['total_sales'] / 30 if sales_data['total_sales'] else 0
    
    # Stock history placeholder - implement actual tracking logic if needed
    stock_history = []
    for date_str in time_periods:
        stock_history.append(product.quantity)  # Simplified example
    
    return {
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'total_sales': sales_data['total_sales'],
        'total_revenue': float(sales_data['total_revenue']),  # Convert Decimal to float
        'sales_velocity': sales_velocity,
        'stock_turnover': product.quantity / sales_velocity if sales_velocity > 0 else 0,
        'profit_margin': float((product.price - product.cost_price) / product.price) if product.price > 0 else 0,
        'stock_history': stock_history,
    }

def inventory_reports(request):
    products = Product.objects.select_related('supplier', 'brand').order_by('name')
    
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)

    categories = Product.objects.values_list('category', flat=True).distinct()
    
    for product in products:
        try:
            last_sale = product.sale_set.latest('date')
            product.days_since_last_sale_display = (timezone.now().date() - last_sale.date).days
        except:
            product.days_since_last_sale_display = "No sales"
        
        product.price = product.cost_price  

    low_stock = Product.objects.filter(quantity__lt=10).select_related('brand')
    overstock = Product.objects.filter(quantity__gt=100).select_related('brand')
   
    for product in low_stock:
        try:
            product.last_restock_date = product.restock_set.latest('restock_date').restock_date
        except:
            product.last_restock_date = "Never"
    
    recent_returns = ProductReturn.objects.select_related('product', 'supplier').order_by('-return_date')[:10]
    
    context = {
        'products': products, 
        'low_stock': low_stock,
        'overstock': overstock,
        'categories': categories,
        'recent_returns': recent_returns, 
    }
    return render(request, 'report/inventory_reports.html', context)

def financial_reports(request):
    revenue = Sale.objects.aggregate(
        total_revenue=Sum(F('quantity_sold') * F('sale_price'))
    )['total_revenue'] or 0
    
    cogs = Sale.objects.aggregate(
        total_cogs=Sum(F('quantity_sold') * F('product__cost_price')) 
    )['total_cogs'] or 0
    
    gross_profit = revenue - cogs
    
    margin = (gross_profit / revenue * 100) if revenue else 0

    revenue_by_brand = Sale.objects.values(
        'product__brand__name'
    ).annotate(
        revenue=Sum(F('quantity_sold') * F('sale_price'))
    ).annotate(
        percentage=Sum(F('quantity_sold') * F('sale_price')) / revenue * 100
    ).order_by('-revenue')

    profitable_products = Sale.objects.values(
        'product__name'
    ).annotate(
        revenue=Sum(F('quantity_sold') * F('sale_price')),
        cogs=Sum(F('quantity_sold') * F('product__cost_price')), 
        profit=Sum(F('quantity_sold') * (F('sale_price') - F('product__cost_price'))),
        margin=Sum(F('quantity_sold') * (F('sale_price') - F('product__cost_price'))) / 
               Sum(F('quantity_sold') * F('sale_price')) * 100
    ).order_by('-profit')[:10] 

    context = {
        'revenue': revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'margin': margin,
        'revenue_by_brand': revenue_by_brand,
        'profitable_products': profitable_products,
    }
    return render(request, 'report/financial_reports.html', context)

def supplier_reports(request):
    # Step 1: Calculate mean and std deviation for restocks and returns
    stats = Supplier.objects.aggregate(
        mean_restocks=Avg('restock__quantity'),
        std_restocks=StdDev('restock__quantity'),
        mean_returns=Avg('productreturn__quantity_returned'),
        std_returns=StdDev('productreturn__quantity_returned'),
    )

    mean_restocks = stats['mean_restocks'] or 1
    std_restocks = stats['std_restocks'] or 1
    mean_returns = stats['mean_returns'] or 1
    std_returns = stats['std_returns'] or 1

    # Step 2: Annotate supplier performance using Composite Score (Z-Score logic)
    supplier_performance = Supplier.objects.annotate(
        total_restocks=Coalesce(
            Subquery(
                Restock.objects.filter(supplier=OuterRef('pk'))
                .values('supplier')
                .annotate(total=Sum('quantity'))
                .values('total')[:1]
            ), 0
        ),
        total_returns=Coalesce(
            Subquery(
                ProductReturn.objects.filter(supplier=OuterRef('pk'))
                .values('supplier')
                .annotate(total=Sum('quantity_returned'))
                .values('total')[:1]
            ), 0
        ),
        total_products=Count('product', distinct=True),
    ).annotate(
        return_rate=ExpressionWrapper(
            F('total_returns') * 100.0 / (F('total_restocks') + 1),
            output_field=FloatField()
        ),
        z_restocks=ExpressionWrapper(
            (F('total_restocks') - mean_restocks) / std_restocks,
            output_field=FloatField()
        ),
        z_returns=ExpressionWrapper(
            (F('total_returns') - mean_returns) / std_returns,
            output_field=FloatField()
        ),
        z_return_rate=ExpressionWrapper(
            (F('return_rate') - 10.0) / 15.0,  # Assume average return rate 10%, std dev 15%
            output_field=FloatField()
        ),
        composite_score=ExpressionWrapper(
            (F('z_restocks') * 1.0 -
            F('z_returns') * 1.0 -
            F('z_return_rate') * 1.0 +
            F('total_products') * 0.5) * 10 + 50,  # Scale to 0-100 range
            output_field=FloatField()
        )
    ).order_by('-composite_score')

    # Step 3: Normalize the composite score to 0-100 for display
    for supplier in supplier_performance:
        # Ensure score is within reasonable bounds
        supplier.performance_score = max(0, min(100, supplier.composite_score))

    # Step 4: Supplier cost analysis
    supplier_cost_analysis = Supplier.objects.annotate(
        avg_price=Avg('product__cost_price'),
        last_restock=Max('restock__restock_date'),
        total_returns=Coalesce(
            Subquery(
                ProductReturn.objects.filter(supplier=OuterRef('pk'))
                .values('supplier')
                .annotate(total=Sum('quantity_returned'))
                .values('total')[:1]
            ), 0
        ),
        top_brand=Subquery(
            Product.objects.filter(supplier=OuterRef('pk'))
            .values('brand__name')
            .annotate(count=Count('id'))
            .order_by('-count')
            .values('brand__name')[:1]
        )
    )

    context = {
        'supplier_performance': supplier_performance,
        'supplier_cost_analysis': supplier_cost_analysis,
    }
    return render(request, 'report/supplier_reports.html', context)

def restock_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST['quantity'])

        product.quantity += quantity
        product.save()

        supplier = product.supplier

        Restock.objects.create(
            product=product,
            quantity=quantity,
            supplier=supplier
        )

        messages.success(request, f'{quantity} units of {product.name} restocked successfully!')

        return redirect('inventory_reports')
    return render(request, 'report/restock_product.html', {'product': product})

def return_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity'))
        reason = request.POST.get('reason', '')

        product = get_object_or_404(Product, id=product_id)
        
        if quantity > product.quantity:
            messages.error(request, f'Cannot return more than available quantity ({product.quantity})')
            return redirect('return_product')

        return_record = ProductReturn.objects.create(
            product=product,
            quantity_returned=quantity,
            reason=reason,
            supplier=product.supplier
        )
        
        return_record.update_product_quantity()

        messages.success(request, f'Successfully returned {quantity} units of {product.name}')
        return redirect('inventory_reports')

    product_id = request.GET.get('product_id')
    initial_product = None
    if product_id:
        initial_product = get_object_or_404(Product, id=product_id)

    products = Product.objects.all()
    return render(request, 'report/return_product.html', {
        'products': products,
        'initial_product': initial_product
    })