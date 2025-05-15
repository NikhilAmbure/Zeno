from django.urls import path
from .views import index, login, logout, register_page
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_page, name='register'),
]