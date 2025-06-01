from django.contrib import admin
from .models import CustomUser, Product, Order, CartItem

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(CartItem)

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