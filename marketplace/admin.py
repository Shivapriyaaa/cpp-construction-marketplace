from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type', 'price', 'rental_price', 'stock_quantity', 'is_available']
    list_filter = ['product_type', 'category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock_quantity', 'is_available']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'product_type')
        }),
        ('Pricing', {
            'fields': ('price', 'rental_price', 'rental_period')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'transaction_type', 'rental_days', 'unit_price', 'total_price']
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'payment_completed', 'created_at']
    list_filter = ['status', 'payment_completed', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'invoice_number']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'invoice_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'invoice_number', 'user', 'status', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_completed',)
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'phone_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_items', 'get_total_price', 'created_at']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)