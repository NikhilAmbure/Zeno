from django.urls import path
from .views import index, login_page, logout, register_page, enter_otp_page, cart_view, wishlist_view, edit_profile_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register_page, name='register'),
    path('enter_otp/<int:user_id>/', enter_otp_page, name="enter_otp"),
    path('cart/', cart_view, name='cart'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('edit-profile/', edit_profile_view, name='edit-profile'),
    path('', index),

]