from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    otp = models.IntegerField(default=0)  # store OTP temporarily

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    


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