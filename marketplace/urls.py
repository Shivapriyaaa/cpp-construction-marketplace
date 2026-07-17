# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views

# urlpatterns = [
#     # ===== ADMIN URLS =====
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/products/', views.admin_products, name='admin_products'),
#     path('admin/products/add/', views.admin_product_add, name='admin_product_add'),
#     path('admin/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
#     path('admin/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
#     path('admin/orders/', views.admin_orders, name='admin_orders'),
#     path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
#     path('admin/orders/<int:order_id>/status/', views.admin_order_status, name='admin_order_status'),
#     path('admin/orders/<int:order_id>/pay/', views.admin_order_pay, name='admin_order_pay'),
#     path('admin/customers/', views.admin_customers, name='admin_customers'),
#     path('admin/inventory/', views.admin_inventory, name='admin_inventory'),
#     path('admin/settings/', views.admin_settings, name='admin_settings'),

#     path('api/cart-count/', views.get_cart_count, name='api_cart_count'),



#         # ===== CATEGORY MANAGEMENT =====
#     path('admin/categories/', views.admin_categories, name='admin_categories'),
#     path('admin/categories/add/', views.admin_category_add, name='admin_category_add'),
#     path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
#     path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),

    
#     # ===== USER AUTH & PROFILE URLS =====
#     # With /users/ prefix
#     path('users/register/', views.register, name='register'),
#     path('users/login/', views.CustomLoginView.as_view(), name='login'),
#     path('users/logout/', views.CustomLogoutView.as_view(), name='logout'),
#     path('users/my-orders/', views.my_orders, name='my_orders'),
#     path('users/cart/', views.view_cart, name='view_cart'),
#     path('users/checkout/', views.checkout, name='checkout'),
#     path('users/payment/<int:order_id>/', views.payment, name='payment'),
#     path('users/order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
#     # Without /users/ prefix (backward compatibility)
#     path('register/', views.register, name='register_alt'),
#     path('login/', views.CustomLoginView.as_view(), name='login_alt'),
#     path('logout/', views.CustomLogoutView.as_view(), name='logout_alt'),
#     path('my-orders/', views.my_orders, name='my_orders_alt'),
#     path('cart/', views.view_cart, name='view_cart_alt'),
#     path('checkout/', views.checkout, name='checkout_alt'),
#     path('payment/<int:order_id>/', views.payment, name='payment_alt'),
#     path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation_alt'),
    
#     # ===== PUBLIC URLS =====
#     path('', views.home, name='home'),
#     path('product/<int:product_id>/', views.product_detail, name='product_detail'),
#     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
#     path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
# ]



from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ===== ADMIN URLS =====
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_product_add, name='admin_product_add'),
    path('admin/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    
    # ===== CATEGORY MANAGEMENT =====
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/add/', views.admin_category_add, name='admin_category_add'),
    path('admin/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # ===== API ENDPOINTS =====
    path('admin/generate-description/', views.generate_description_api, name='generate_description'),
    
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<int:order_id>/status/', views.admin_order_status, name='admin_order_status'),
    path('admin/orders/<int:order_id>/pay/', views.admin_order_pay, name='admin_order_pay'),
    path('admin/customers/', views.admin_customers, name='admin_customers'),
    path('admin/inventory/', views.admin_inventory, name='admin_inventory'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    
    # ===== USER AUTH & PROFILE URLS =====
    path('users/register/', views.register, name='register'),
    path('users/login/', views.CustomLoginView.as_view(), name='login'),
    path('users/logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('users/my-orders/', views.my_orders, name='my_orders'),
    path('users/cart/', views.view_cart, name='view_cart'),
    path('users/checkout/', views.checkout, name='checkout'),
    path('users/payment/<int:order_id>/', views.payment, name='payment'),
    path('users/order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # ===== PUBLIC URLS =====
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('api/cart-count/', views.get_cart_count, name='api_cart_count'),
]