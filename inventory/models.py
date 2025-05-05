from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Brand(models.Model):
    BRAND_CHOICES = [
        ('Nike', 'Nike'),
        ('Adidas', 'Adidas'),
        ('Puma', 'Puma'),
        ('New Balance', 'New Balance'),
        ('Vans', 'Vans'),
        ('Converse', 'Converse'),
    ]
    name = models.CharField(max_length=100, choices=BRAND_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2) 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name
    def get_stock_value(self):
        return self.price * self.quantity
    
    @property
    def days_since_last_sale(self):
        last_sale = self.sale_set.order_by('-sale_date').first()
        if last_sale:
            return (timezone.now() - last_sale.sale_date).days
        return "No sales yet"



class Restock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    restock_date = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.quantity} of {self.product.name} restocked on {self.restock_date}'
    class Meta:
        get_latest_by = 'restock_date'


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} sold on {self.sale_date}"

    def update_product_quantity(self):
        product = self.product
        product.quantity -= self.quantity_sold
        product.save()
    def get_total_price(self):
        return self.quantity_sold * self.sale_price
    
class ProductReturn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_returned = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    return_date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity_returned} of {self.product.name} returned to {self.supplier.name} on {self.return_date}"

    def update_product_quantity(self):
        product = self.product
        product.quantity = max(product.quantity - self.quantity_returned, 0)  
        product.save()
