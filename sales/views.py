from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from inventory.models import Product, Sale
import json
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def sales_view(request):
    if request.method == 'GET':
        query = request.GET.get('search', '')
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__name__icontains=query) | 
            Q(category__icontains=query)
        )
        return render(request, 'sales/sales.html', {'products': products})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_items = data.get('selected_items', [])
            
            if not selected_items:
                return JsonResponse({'success': False, 'message': 'No items selected'})
            
            sale_records = []
            total_amount = 0
            
            for item in selected_items:
                product = Product.objects.get(id=item['productId'])
                quantity = item['quantity']
                
                if product.quantity < quantity:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Not enough stock for {product.name} (Available: {product.quantity})'
                    })

                sale = Sale.objects.create(
                    product=product,
                    quantity_sold=quantity,
                    sale_price=product.price
                )
                sale.update_product_quantity()
                sale_records.append(sale)
                total_amount += product.price * quantity
            
            return JsonResponse({
                'success': True,
                'sale_ids': [sale.id for sale in sale_records],
                'total_amount': total_amount,
                'message': 'Sale processed successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def sales_receipt(request):
    sale_ids = request.GET.get('sale_ids', '').split(',')
    total_amount = request.GET.get('total', 0)
    sale_ids = [id for id in sale_ids if id]
    
    sales = Sale.objects.filter(id__in=sale_ids).select_related('product')

    sale_date = sales[0].sale_date if sales else None
    
    return render(request, 'sales/sales_receipt.html', {
        'sales': sales,
        'total_amount': total_amount,
        'sale_date': sale_date
    })

def sales_history_view(request):
    sort_by = request.GET.get('sort', '-sale_date')

    sales = Sale.objects.all().order_by(sort_by)
    
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'sales/sales_history.html', {
        'page_obj': page_obj,
        'sales': page_obj.object_list
    })