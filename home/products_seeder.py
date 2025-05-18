

import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
django.setup()

from home.models import Category, SubCategory, Product

faker = Faker()

categories = {
    "Electronics": ["Desktop", "Laptop", "Camera", "Tablet", "Headphone", "Smart Watch", "Smart TV", "Keyboard", "Mouse", "Microphone"],
    "Men's": ["Formal", "Casual", "Sports", "Jacket", "Sunglasses", "Shirt", "Shorts & Jeans", "Safety Shoes", "Wallet"],
    "Women's": ["Formal", "Casual", "Perfume", "Cosmetics", "Bags", "Dress & Frock", "Earrings", "Necklace", "Makeup Kit"],
    "Jewelry": ["Earrings", "Couple Rings", "Necklace", "Bracelets"],
    "Perfume": ["Clothes Perfume", "Deodorant", "Flower Fragrance", "Air Freshener"]
}

def run():
    # Create categories and subcategories
    for cat, subcats in categories.items():
        category_obj, _ = Category.objects.get_or_create(name=cat)
        for sub in subcats:
            SubCategory.objects.get_or_create(category=category_obj, name=sub)

    subcategories = SubCategory.objects.all()

    # Create fake products
    for _ in range(100):
        subcat = random.choice(subcategories)
        name = faker.word().capitalize() + " " + subcat.name
        desc = faker.text(max_nb_chars=150)
        price = round(random.uniform(10, 500), 2)
        old_price = round(price + random.uniform(5, 50), 2)

        Product.objects.create(
            name=name,
            description=desc,
            category=subcat,
            price=price,
            old_price=old_price,
            is_new=random.choice([True, False]),
            is_trending=random.choice([True, False]),
            is_top_rated=random.choice([True, False]),
        )

    print("✅ 100 products created with categories and subcategories!")
