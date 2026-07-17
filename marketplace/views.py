from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User  # IMPORTANT: For User model
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone  # IMPORTANT: For timezone operations
from decimal import Decimal
from .models import Product, Cart, CartItem, Order, OrderItem, Category
from .forms import UserRegisterForm, CheckoutForm, ProductForm
import uuid

# ===================== PUBLIC VIEWS =====================

def home(request):
    products = Product.objects.filter(is_available=True, stock_quantity__gt=0)
    categories = Category.objects.all()
    
    # Filter by type
    sale_products = products.filter(product_type__in=['sale', 'both'])[:8]
    rent_products = products.filter(product_type__in=['rent', 'both'])[:8]
    
    context = {
        'products': products,
        'categories': categories,
        'sale_products': sale_products,
        'rent_products': rent_products,
    }
    return render(request, 'marketplace/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'marketplace/product_detail.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Construction Mart.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# ===================== CART VIEWS =====================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity', 1))
        rental_days = request.POST.get('rental_days')
        
        # Check stock
        if quantity > product.stock_quantity:
            messages.error(request, 'Not enough stock available!')
            return redirect('product_detail', product_id=product.id)
        
        if transaction_type == 'rent' and product.product_type not in ['rent', 'both']:
            messages.error(request, 'This product is not available for rent.')
            return redirect('product_detail', product_id=product.id)
        
        if transaction_type == 'sale' and product.product_type not in ['sale', 'both']:
            messages.error(request, 'This product is not available for purchase.')
            return redirect('product_detail', product_id=product.id)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            transaction_type=transaction_type,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                messages.error(request, 'Not enough stock available!')
                return redirect('product_detail', product_id=product.id)
            cart_item.quantity = new_quantity
        
        if transaction_type == 'rent' and rental_days:
            cart_item.rental_days = int(rental_days)
        
        cart_item.save()
        messages.success(request, f'Added {product.name} to cart!')
    
    return redirect('product_detail', product_id=product.id)



# @login_required
# def view_cart(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = cart.cartitem_set.all()
    
#     total = cart.get_total_price()
    
#     context = {
#         'cart_items': cart_items,
#         'total': total,
#     }
#     return render(request, 'marketplace/cart.html', context)

from taxation_lib import calculate_total_with_tax, calculate_tax


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    subtotal = cart.get_total_price()
    tax_amount = calculate_tax(subtotal)
    total_with_tax = calculate_total_with_tax(subtotal)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total': total_with_tax,
    }
    return render(request, 'marketplace/cart.html', context)







@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock_quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, 'Not enough stock available!')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart.')
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    
    return redirect('view_cart')

# ===================== ORDER VIEWS =====================





# @login_required
# def checkout(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = cart.cartitem_set.all()
    
#     if not cart_items:
#         messages.warning(request, 'Your cart is empty!')
#         return redirect('home')
    
#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 # Create order
#                 total = cart.get_total_price()
#                 order = Order.objects.create(
#                     user=request.user,
#                     total_amount=total,
#                     shipping_address=f"{form.cleaned_data['address']}, {form.cleaned_data['city']}, {form.cleaned_data['state']} - {form.cleaned_data['pincode']}",
#                     phone_number=form.cleaned_data['phone'],
#                     status='pending'
#                 )
                
#                 # Create order items
#                 for item in cart_items:
#                     unit_price = item.product.price if item.transaction_type == 'sale' else item.product.rental_price
#                     total_price = item.get_total_price()
                    
#                     OrderItem.objects.create(
#                         order=order,
#                         product=item.product,
#                         quantity=item.quantity,
#                         transaction_type=item.transaction_type,
#                         rental_days=item.rental_days,
#                         unit_price=unit_price,
#                         total_price=total_price
#                     )
                    
#                     # Deduct from stock
#                     item.product.stock_quantity -= item.quantity
#                     item.product.save()
                
#                 # Clear cart
#                 cart_items.delete()
            
#             # Send SNS notification to admin for new order
#             try:
#                 sns_service = SNSService()
#                 result = sns_service.send_admin_new_order_notification(order)
#                 if result['success']:
#                     print(f"Admin notification sent: {result['message_id']}")
#                 else:
#                     print(f"Failed to send admin notification: {result['error']}")
#             except Exception as e:
#                 print(f"SNS Error: {e}")
            
#             return redirect('payment', order_id=order.id)
#     else:
#         initial_data = {
#             'full_name': f"{request.user.first_name} {request.user.last_name}",
#             'email': request.user.email,
#         }
#         form = CheckoutForm(initial=initial_data)
    
#     context = {
#         'cart_items': cart_items,
#         'total': cart.get_total_price(),
#         'form': form,
#     }
#     return render(request, 'marketplace/checkout.html', context)




from taxation_lib import calculate_total_with_tax, calculate_tax

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('home')
    
    # Calculate totals with tax
    subtotal = cart.get_total_price()
    tax_amount = calculate_tax(subtotal)
    total_with_tax = calculate_total_with_tax(subtotal)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create order with tax-included total
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_with_tax,  # Now includes tax
                    shipping_address=f"{form.cleaned_data['address']}, {form.cleaned_data['city']}, {form.cleaned_data['state']} - {form.cleaned_data['pincode']}",
                    phone_number=form.cleaned_data['phone'],
                    status='pending'
                )
                
                # Create order items
                for item in cart_items:
                    unit_price = item.product.price if item.transaction_type == 'sale' else item.product.rental_price
                    total_price = item.get_total_price()
                    
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        transaction_type=item.transaction_type,
                        rental_days=item.rental_days,
                        unit_price=unit_price,
                        total_price=total_price
                    )
                    
                    # Deduct from stock
                    item.product.stock_quantity -= item.quantity
                    item.product.save()
                
                # Clear cart
                cart_items.delete()
            
            # Send SNS notification to admin for new order
            try:
                sns_service = SNSService()
                result = sns_service.send_admin_new_order_notification(order)
                if result['success']:
                    print(f"Admin notification sent: {result['message_id']}")
                else:
                    print(f"Failed to send admin notification: {result['error']}")
            except Exception as e:
                print(f"SNS Error: {e}")
            
            return redirect('payment', order_id=order.id)
    else:
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total': total_with_tax,
        'form': form,
    }
    return render(request, 'marketplace/checkout.html', context)








import boto3
from django.conf import settings

class SNSService:
    def __init__(self):
        # Uses IAM role or AWS credentials from environment
        self.sns_client = boto3.client(
            'sns',
            region_name="us-east-1"
        )
    
    def send_admin_new_order_notification(self, order):
        """
        Send new order notification to admin via SNS
        """
        subject = f"New Order Received - {order.order_number}"
        
        message = f"""
New Order Alert

Order Details:
--------------
Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y %H:%M')}
Total Amount: ${order.total_amount:.2f}
Status: {order.get_status_display()}

Customer Information:
--------------------
Name: {order.user.get_full_name() or order.user.username}
Email: {order.user.email}
Phone: {order.phone_number}
Shipping Address: {order.shipping_address}

Items Ordered:
--------------
"""
        for item in order.items.all():
            message += f"  - {item.product.name} x {item.quantity} = ${item.total_price:.2f}\n"
        
        message += f"""

Action Required:
View Order: http://http://constructionmarketplace.us-east-1.elasticbeanstalk.com/admin/orders/{order.id}/

Best regards,
ConstructionMart System
"""
        
        try:
            response = self.sns_client.publish(
                TopicArn="arn:aws:sns:us-east-1:250401826260:x24266388-cpp-sns",
                Subject=subject,
                Message=message
            )
            return {
                'success': True,
                'message_id': response.get('MessageId')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }






# @login_required
# def payment(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
    
#     if order.payment_completed:
#         messages.warning(request, 'This order has already been paid.')
#         return redirect('order_confirmation', order_id=order.id)
    
#     if request.method == 'POST':
#         # Simulate payment processing
#         with transaction.atomic():
#             order.payment_completed = True
#             order.status = 'paid'
#             order.save()
            
#             # Generate invoice number
#             order.invoice_number = f"INV-{order.id:06d}-{order.order_number}"
#             order.save()
        
#         # Send SNS notification to admin
#         try:
#             sns_service = SNSService()
#             result = sns_service.send_admin_new_order_notification(order)
#             if result['success']:
#                 print(f"Admin notification sent: {result['message_id']}")
#             else:
#                 print(f"Failed to send admin notification: {result['error']}")
#         except Exception as e:
#             # Log error but don't stop the payment process
#             print(f"SNS Error: {e}")
        
#         messages.success(request, 'Payment successful! Your order has been placed.')
#         return redirect('order_confirmation', order_id=order.id)
    
#     context = {
#         'order': order,
#         'total': order.total_amount,
#     }
#     return render(request, 'marketplace/payment.html', context)





from taxation_lib import calculate_total_with_tax, calculate_tax

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_completed:
        messages.warning(request, 'This order has already been paid.')
        return redirect('order_confirmation', order_id=order.id)
    
    if request.method == 'POST':
        # Simulate payment processing
        with transaction.atomic():
            order.payment_completed = True
            order.status = 'paid'
            order.save()
            
            # Generate invoice number
            order.invoice_number = f"INV-{order.id:06d}-{order.order_number}"
            order.save()
        
        # Send SNS notification to admin
        try:
            sns_service = SNSService()
            result = sns_service.send_admin_new_order_notification(order)
            if result['success']:
                print(f"Admin notification sent: {result['message_id']}")
            else:
                print(f"Failed to send admin notification: {result['error']}")
        except Exception as e:
            # Log error but don't stop the payment process
            print(f"SNS Error: {e}")
        
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('order_confirmation', order_id=order.id)
    
    # Show total with tax on payment page
    total_with_tax = order.total_amount  # Already includes tax from checkout
    
    context = {
        'order': order,
        'total': total_with_tax,
    }
    return render(request, 'marketplace/payment.html', context)




@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'marketplace/order_confirmation.html', context)

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'marketplace/orders.html', context)

# ===================== ADMIN VIEWS =====================

@staff_member_required
def admin_dashboard(request):
    # Stats
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()  # User is now imported
    
    # Calculate revenue
    total_revenue = Order.objects.filter(payment_completed=True).aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    
    
    # Calculate tax collected (10% of revenue)
    tax_collected = calculate_tax(total_revenue)
    revenue_without_tax = total_revenue - tax_collected
    
    # Recent activities (simplified - you can enhance this with real data)
    recent_activities = [
        {'icon': 'fa-box', 'icon_color': 'blue', 'text': 'New product added: Premium Cement', 'time': '2 hours ago'},
        {'icon': 'fa-shopping-bag', 'icon_color': 'green', 'text': 'New order #ORD-2026-001', 'time': '5 hours ago'},
        {'icon': 'fa-user', 'icon_color': 'orange', 'text': 'New customer registered: John Doe', 'time': '1 day ago'},
        {'icon': 'fa-warehouse', 'icon_color': 'red', 'text': 'Low stock alert: Drill Machine (5 left)', 'time': '2 days ago'},
    ]
    
    # Get actual new counts
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    new_products = Product.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    ).count()
    
    new_orders = Order.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    ).count()
    
    new_customers = User.objects.filter(
        is_staff=False,
        date_joined__year=current_year,
        date_joined__month=current_month
    ).count()
    
    # Calculate revenue growth (simplified)
    revenue_growth = 12.5
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'tax_collected': tax_collected,
        'revenue_without_tax': revenue_without_tax,
        'new_products': new_products,
        'new_orders': new_orders,
        'new_customers': new_customers,
        'revenue_growth': revenue_growth,
        'recent_activities': recent_activities,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@staff_member_required
def admin_products(request):
    products_list = Product.objects.all().order_by('-created_at')
    
    # Apply filters
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    product_type = request.GET.get('type', '')
    stock_filter = request.GET.get('stock', '')
    
    if search:
        products_list = products_list.filter(name__icontains=search)
    if category:
        products_list = products_list.filter(category_id=category)
    if product_type:
        products_list = products_list.filter(product_type=product_type)
    if stock_filter == 'in':
        products_list = products_list.filter(stock_quantity__gt=10)
    elif stock_filter == 'low':
        products_list = products_list.filter(stock_quantity__lte=10, stock_quantity__gt=0)
    elif stock_filter == 'out':
        products_list = products_list.filter(stock_quantity=0)
    
    paginator = Paginator(products_list, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'admin_dashboard/products.html', context)



import json
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from .forms import ProductForm
from .models import Product


# =====================================================
# API Gateway URL
# =====================================================

LAMBDA_API_URL = "https://dp6qr5lzt6.execute-api.us-east-1.amazonaws.com/default/x24266388-lambda-cpp"


# =====================================================
# Helper Function
# =====================================================

def generate_description_from_lambda(product_name,
                                     category="Construction Equipment",
                                     product_type="default",
                                     features=None):

    if features is None:
        features = []

    payload = {
        "product_name": product_name,
        "category": category,
        "product_type": product_type,
        "features": features
    }

    try:

        response = requests.post(
            LAMBDA_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        # Lambda Proxy Integration
        if isinstance(result, dict) and "body" in result:

            body = result["body"]

            if isinstance(body, str):
                body = json.loads(body)

            return body

        return result

    except requests.exceptions.RequestException as e:

        print("Lambda API Error:", e)

        return {
            "error": str(e)
        }


# =====================================================
# AJAX Description Generator
# =====================================================

@staff_member_required
@csrf_exempt
def generate_description_api(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method Not Allowed"},
            status=405
        )

    try:

        data = json.loads(request.body)

        product_name = data.get("product_name")

        if not product_name:
            return JsonResponse(
                {"error": "Product name is required"},
                status=400
            )

        result = generate_description_from_lambda(
            product_name=product_name,
            category=data.get(
                "category",
                "Construction Equipment"
            ),
            product_type=data.get(
                "product_type",
                "default"
            ),
            features=data.get(
                "features",
                []
            )
        )

        if result.get("error"):
            return JsonResponse(result, status=500)

        return JsonResponse(result)

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )


# =====================================================
# ADMIN ADD PRODUCT
# =====================================================

@staff_member_required
def admin_product_add(request):

    if request.method == "POST":

        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():

            product = form.save(commit=False)

            # Auto Generate Description
            if not product.description:

                result = generate_description_from_lambda(
                    product_name=product.name,
                    category=product.category.name if product.category else "Construction Equipment",
                    product_type="default",
                    features=[]
                )

                if result.get("description"):
                    product.description = result["description"]

            product.save()

            messages.success(
                request,
                "Product added successfully!"
            )

            return redirect("admin_products")

    else:

        form = ProductForm()

    return render(
        request,
        "admin_dashboard/product_form.html",
        {
            "form": form
        }
    )


# =====================================================
# ADMIN EDIT PRODUCT
# =====================================================

@staff_member_required
def admin_product_edit(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product updated successfully!"
            )

            return redirect("admin_products")

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "admin_dashboard/product_form.html",
        {
            "form": form,
            "product": product
        }
    )
    
    

@staff_member_required
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('admin_products')

# @staff_member_required
# def admin_orders(request):
#     orders_list = Order.objects.all().order_by('-created_at')
#     paginator = Paginator(orders_list, 10)
#     page = request.GET.get('page')
#     orders = paginator.get_page(page)
    
#     context = {'orders': orders}
#     return render(request, 'admin_dashboard/orders.html', context)









from taxation_lib import calculate_tax

@staff_member_required
def admin_orders(request):
    orders_list = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders_list, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    # Calculate tax for each order
    for order in orders:
        order.tax_amount = calculate_tax(order.total_amount)
        order.subtotal = order.total_amount - order.tax_amount
    
    context = {'orders': orders}
    return render(request, 'admin_dashboard/orders.html', context)






# @staff_member_required
# def admin_order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     context = {'order': order}
#     return render(request, 'admin_dashboard/order_detail.html', context)










from taxation_lib import calculate_tax

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate tax breakdown
    order.tax_amount = calculate_tax(order.total_amount)
    order.subtotal = order.total_amount - order.tax_amount
    
    context = {'order': order}
    return render(request, 'admin_dashboard/order_detail.html', context)



@staff_member_required
def admin_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS):
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully!')
    return redirect('admin_order_detail', order_id=order.id)

@staff_member_required
def admin_order_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.payment_completed = True
        order.status = 'paid'
        order.save()
        messages.success(request, 'Order marked as paid!')
    return redirect('admin_order_detail', order_id=order.id)

@staff_member_required
def admin_customers(request):
    customers = User.objects.filter(is_staff=False).annotate(
        orders_count=Count('order'),
        total_spent=Sum('order__total_amount', filter=Q(order__payment_completed=True))
    ).order_by('-date_joined')
    
    context = {'customers': customers}
    return render(request, 'admin_dashboard/customers.html', context)

@staff_member_required
def admin_inventory(request):
    products = Product.objects.all().order_by('stock_quantity')
    
    total_products = products.count()
    total_stock = products.aggregate(total=Sum('stock_quantity'))['total'] or 0
    low_stock_count = products.filter(stock_quantity__lte=10, stock_quantity__gt=0).count()
    out_of_stock_count = products.filter(stock_quantity=0).count()
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'admin_dashboard/inventory.html', context)

@staff_member_required
def admin_settings(request):
    return render(request, 'admin_dashboard/settings.html')








# ===================== CATEGORY MANAGEMENT VIEWS =====================

@staff_member_required
def admin_categories(request):
    """Display all categories with product counts"""
    categories = Category.objects.all().annotate(
        product_count=Count('product')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'admin_dashboard/categories.html', context)

@staff_member_required
def admin_category_add(request):
    """Add a new category"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'fa-box')
        description = request.POST.get('description', '')
        
        if not name:
            messages.error(request, 'Category name is required!')
            return redirect('admin_category_add')
        
        # Check if category already exists
        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Category "{name}" already exists!')
            return redirect('admin_category_add')
        
        Category.objects.create(
            name=name,
            icon=icon,
            description=description
        )
        messages.success(request, f'Category "{name}" added successfully!')
        return redirect('admin_categories')
    
    context = {'category': None}
    return render(request, 'admin_dashboard/category_form.html', context)

@staff_member_required
def admin_category_edit(request, category_id):
    """Edit an existing category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'fa-box')
        description = request.POST.get('description', '')
        
        if not name:
            messages.error(request, 'Category name is required!')
            return redirect('admin_category_edit', category_id=category_id)
        
        # Check if another category with same name exists
        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            messages.error(request, f'Category "{name}" already exists!')
            return redirect('admin_category_edit', category_id=category_id)
        
        category.name = name
        category.icon = icon
        category.description = description
        category.save()
        
        messages.success(request, f'Category "{name}" updated successfully!')
        return redirect('admin_categories')
    
    context = {'category': category}
    return render(request, 'admin_dashboard/category_form.html', context)

@staff_member_required
def admin_category_delete(request, category_id):
    """Delete a category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        # Check if category has products
        if category.product_set.exists():
            messages.error(
                request, 
                f'Cannot delete "{category.name}" because it has {category.product_set.count()} products. Please reassign or delete the products first.'
            )
            return redirect('admin_categories')
        
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
    
    return redirect('admin_categories')


from django.http import JsonResponse

@login_required
def get_cart_count(request):
    """API endpoint to get cart count"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    count = cart.get_total_items()
    return JsonResponse({'count': count})




# ===================== CUSTOM LOGIN/LOGOUT =====================

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        if self.request.user.is_staff:
            return '/admin/dashboard/'
        return '/'

class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'
    next_page = 'home'
    
    def get(self, request, *args, **kwargs):
        # Handle GET requests for logout (when users click logout link)
        logout(request)
        messages.success(request, 'You have been logged out successfully!')
        return redirect('home')
    
    def post(self, request, *args, **kwargs):
        # Handle POST requests for logout
        logout(request)
        messages.success(request, 'You have been logged out successfully!')
        return redirect('home')