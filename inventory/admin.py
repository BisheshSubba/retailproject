from django.contrib import admin
from .models import Product, Supplier, Sale

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Sale)
