from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.utils import timezone
from django.conf import settings

# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.IntegerField(default=0)  # store OTP temporarily

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



# models.py

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/')
    secondary_image = models.ImageField(upload_to='products/', null=True, blank=True)

    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_new = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_top_rated = models.BooleanField(default=False)
    new_prod = models.BooleanField(default=False)
    dotd = models.BooleanField(default=False)
    best_sellers = models.BooleanField(default=False)

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    def __str__(self):
        return self.name




class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate items for same user/product

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.user.email})"

    @property
    def total_price(self):
        return self.product.price * self.quantity




# # Order Model
# class Order(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
#     product_name = models.CharField(max_length=255)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     ordered_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, default='pending')

#     def __str__(self):
#         return f"Order {self.id} by {self.user.email}"