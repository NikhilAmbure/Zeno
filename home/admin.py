from django.contrib import admin
from .models import CustomUser, Product

# Register your models here.

admin.site.register(CustomUser)


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