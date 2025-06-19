# Dummy JSON API: https://dummyjson.com/docs/products

import os
import django
import requests
import cloudinary.uploader
from decimal import Decimal

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Zeno.settings')  
django.setup()

from home.models import Product, SubCategory  

# Mapping DummyJSON categories to subcategories
CATEGORY_MAP = {
    "smartphones": "Smart Watch",
    "laptops": "Laptop",
    "mens-shirts": "Shirt",
    "womens-dresses": "Dress & Frock",
    "womens-shoes": "Casual",
    "mens-shoes": "Safety Shoes",
    "mens-watches": "Watch",
    "womens-watches": "Watch",
    "womens-bags": "Bags",
    "womens-jewellery": "Jewelry",
    "sunglasses": "Sunglasses",
}


def get_or_create_subcategory(name):
    try:
        return SubCategory.objects.get(name__iexact=name)
    except SubCategory.DoesNotExist:
        print(f"❌ SubCategory '{name}' does not exist. Skipping.")
        return None

def upload_image_to_cloudinary(url, public_id):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return cloudinary.uploader.upload(response.content, public_id=public_id)['public_id']
    except Exception as e:
        print(f"⚠️ Failed to upload image: {e}")
        return None

def import_products():
    res = requests.get('https://dummyjson.com/products?limit=100').json()
    count = 0

    for product in res['products']:
        category = product['category']
        if category not in CATEGORY_MAP:
            continue

        subcategory_name = CATEGORY_MAP[category]
        subcat = get_or_create_subcategory(subcategory_name)
        if not subcat:
            continue

        image_url = product['images'][0]
        sec_image_url = product['images'][1] if len(product['images']) > 1 else product['images'][0]

        image_public_id = upload_image_to_cloudinary(image_url, f"{product['title']}_1")
        sec_image_public_id = upload_image_to_cloudinary(sec_image_url, f"{product['title']}_2")

        Product.objects.get_or_create(
            name=product['title'],
            defaults={
                'price': Decimal(product['price']),
                'old_price': Decimal(product['price']) * Decimal(1.2),
                'description': product['description'],
                'image': image_public_id,
                'secondary_image': sec_image_public_id,
                'category': subcat,
                'is_new': True,
                'is_trending': product['rating'] >= 4.3,
                'is_top_rated': product['rating'] >= 4.5,
            }
        )
        count += 1
        print(f"✅ Imported: {product['title']}")

    print(f"\n🎉 Done! Imported {count} products.")

if __name__ == "__main__":
    import_products()