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
    slug = models.SlugField(blank=True, null=True)

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



# models.py

# Suggested improvements to your Order model in models.py

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_CHOICES = (
        ('RAZORPAY', 'Razorpay'),
        ('COD', 'Cash On Delivery'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')

    # To save delivery info even if user changes it later
    name = models.CharField(max_length=100, default='Unknown')
    email = models.EmailField(default="unknown@example.com")
    phone = models.CharField(max_length=20, default="0000000000000000")
    address = models.TextField(default='Not Provided')

    # items = models.ManyToManyField(CartItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    is_paid = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    # Optional fields that your template expects
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"
    
    @property
    def total_items(self):
        """Calculate total number of items in the order"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def status_display(self):
        """Get human-readable status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
    
    @property
    def subtotal(self):
        return self.price * self.quantity

class WishlistItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    @classmethod
    def get_count(cls, user):
        if user.is_authenticated:
            return cls.objects.filter(user=user).count()
        return 0