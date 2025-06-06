from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', index, name='index'),
    path('login/', login_page, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register_page, name='register'),
    path('enter_otp/<int:user_id>/', enter_otp_page, name='enter_otp'),

    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', update_cart_quantity, name='update_cart_quantity'),

    path('wishlist/', wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:item_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('move-to-cart/<int:product_id>/', move_to_cart, name='move_to_cart'),
    path('clear-wishlist/', clear_wishlist, name='clear_wishlist'),

    path('edit-profile/', edit_profile_view, name='edit-profile'),
    path('my-orders/', my_orders, name='my-orders'),
    # path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('blog/', blog_view, name='blog'),

    path('search/', search_results, name='search_results'),
    path('checkout/', checkout_page, name='checkout'),
    path('select-payment-method/', select_payment_method, name='select_payment_method'),
    path('place-order/cod/', place_order_cod, name='place_order_cod'),
    path('razorpay-payment/', razorpay_payment, name='razorpay_payment'),
    path('handle-payment/', handle_payment, name='handle_payment'),
    path('receipt/<int:order_id>/', generate_receipt, name='generate_receipt'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),

]
