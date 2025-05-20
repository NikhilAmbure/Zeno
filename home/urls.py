from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register_page, name='register'),
    path('enter_otp/<int:user_id>/', enter_otp_page, name="enter_otp"),
    path('cart/', cart_view, name='cart'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('edit-profile/', edit_profile_view, name='edit-profile'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('', index, name='index'),

]