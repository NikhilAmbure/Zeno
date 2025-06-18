import json
from home.models import Product, SubCategory 

with open('home/products.json') as f:
    products = json.load(f)

for item in products:
    try:
        category = SubCategory.objects.get(name=item['category'])
        product = Product.objects.create(
            name=item['name'],
            price=item['price'],
            description=item['description'],
            image=item['image'],
            secondary_image=item['secondary_image'],
            category=category,
            old_price=item['old_price'],
            is_new=item['is_new'],
            is_trending=item['is_trending'],
            is_top_rated=item['is_top_rated'],
            new_prod=item['new_prod'],
            dotd=item['dotd'],
            best_sellers=item['best_sellers']
        )
        print(f"Added: {product.name}")
    except SubCategory.DoesNotExist:
        print(f"SubCategory not found: {item['category']}")
