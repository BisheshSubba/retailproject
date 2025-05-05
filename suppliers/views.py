from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import Product, Supplier, Sale
from django.utils import timezone
from django.contrib import messages

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        name = request.POST['name']
        contact_info = request.POST['contact_info']
        address = request.POST['address']

        Supplier.objects.create(name=name, contact_info=contact_info, address=address)
        messages.success(request, "Supplier added successfully!")
        return redirect('supplier_list')

    return render(request, 'suppliers/add_supplier.html')

def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.name = request.POST['name']
        supplier.contact_info = request.POST['contact_info']
        supplier.address = request.POST['address']
        supplier.save()

        messages.success(request, "Supplier updated successfully!")
        return redirect('supplier_list')

    return render(request, 'suppliers/update_supplier.html', {'supplier': supplier})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    messages.success(request, "Supplier deleted successfully!")
    return redirect('supplier_list')
