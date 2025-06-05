from django.contrib import admin
from .models import CustomUser, Product, OrderItem, Order, CartItem, WishlistItem

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(WishlistItem)

@admin.register(Product)
class CustomProduct(admin.ModelAdmin):
    list_display=(
        "name",
        "price",
        "old_price",
        "category",
    )

    search_fields=(
        'name',
        'price',
        'old_price',
        'category'
    )