from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Supplier, Sale, Restock,Brand
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator

def product_list(request):
    categories = Product.objects.values_list('category', flat=True).distinct()
    brands = Brand.objects.all()
    
    products = Product.objects.all()
    
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)
    
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'inventory/product_list.html', context)
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        price = request.POST['price']
        cost_price = request.POST['cost_price']  
        quantity = request.POST['quantity']
        supplier_id = request.POST['supplier']
        brand_id = request.POST['brand']
        supplier = Supplier.objects.get(id=supplier_id)
        brand = Brand.objects.get(id=brand_id)
        image = request.FILES.get('image')

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            cost_price=cost_price, 
            quantity=quantity,
            supplier=supplier,
            brand=brand,
            image=image
        )

        messages.success(request, "Product added successfully!")
        return redirect('product_list')

    suppliers = Supplier.objects.all()
    brands = Brand.objects.all()
    return render(request, 'inventory/add_product.html', {'suppliers': suppliers, 'brands': brands})


def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        price = request.POST['price']
        cost_price = request.POST['cost_price']
        quantity = request.POST['quantity']
        supplier_id = request.POST['supplier']
        brand_id = request.POST['brand']
        supplier = Supplier.objects.get(id=supplier_id)
        brand = Brand.objects.get(id=brand_id) 
        image = request.FILES.get('image')  

        product.name = name
        product.category = category
        product.price = price
        product.cost_price = cost_price
        product.quantity = quantity
        product.supplier = supplier
        product.brand = brand 

        if image:
            product.image = image
        
        product.save()

        messages.success(request, "Product updated successfully!")
        return redirect('product_list')

    suppliers = Supplier.objects.all()
    brands = Brand.objects.all()
    return render(request, 'inventory/update_product.html', {'product': product, 'suppliers': suppliers, 'brands': brands})



def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('product_list')

def restock_history(request):
    restocks = Restock.objects.all().order_by('-restock_date')
    return render(request, 'inventory/restock_history.html', {'restocks': restocks})
