from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('both', 'Both'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='sale')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rental_period = models.CharField(max_length=50, blank=True, help_text="e.g., per day, per week")
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', args=[str(self.id)])

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total_price(self):
        total = Decimal('0.00')
        for item in self.cartitem_set.all():
            total += item.get_total_price()
        return total
    
    def get_total_items(self):
        return self.cartitem_set.count()

class CartItem(models.Model):
    TRANSACTION_TYPES = [
        ('sale', 'Buy'),
        ('rent', 'Rent'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    rental_days = models.PositiveIntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        if self.transaction_type == 'sale':
            return self.product.price * self.quantity
        else:
            if self.product.rental_price and self.rental_days:
                return self.product.rental_price * self.quantity * self.rental_days
            return Decimal('0.00')

# class Order(models.Model):
#     ORDER_STATUS = [
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order_number = models.CharField(max_length=50, unique=True, blank=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
#     shipping_address = models.TextField()
#     phone_number = models.CharField(max_length=15)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     payment_completed = models.BooleanField(default=False)
#     invoice_number = models.CharField(max_length=50, blank=True)
    
#     def __str__(self):
#         return f"Order #{self.order_number} - {self.user.username}"
    
#     def save(self, *args, **kwargs):
#         if not self.order_number:
#             self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{User.objects.count():06d}"
#         if not self.invoice_number and self.payment_completed:
#             self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{self.id:06d}"
#         super().save(*args, **kwargs)


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_completed = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number using timestamp and random number
            import random
            import string
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"ORD-{timestamp}-{random_suffix}"
        
        if not self.invoice_number and self.payment_completed:
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{self.id:06d}"
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    TRANSACTION_TYPES = [
        ('sale', 'Buy'),
        ('rent', 'Rent'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    rental_days = models.PositiveIntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"