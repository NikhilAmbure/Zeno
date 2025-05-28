import os
import django
import random
from faker import Faker
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from home.models import Product, SubCategory

fake = Faker()

subcategories = list(SubCategory.objects.all())

def create_dummy_image():
    img = Image.new('RGB', (500, 500), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue(), f'{fake.word()}.jpg')

def add_fake_products(count=50):
    for _ in range(count):
        subcat = random.choice(subcategories)
        price = round(random.uniform(100, 1000), 2)
        old_price = price + random.randint(20, 200) if random.choice([True, False]) else None

        product = Product(
            name=fake.unique.word().capitalize() + " " + subcat.name,
            price=price,
            old_price=old_price,
            description=fake.text(max_nb_chars=200),
            category=subcat,
            is_new=random.choice([True, False]),
            is_trending=random.choice([True, False]),
            is_top_rated=random.choice([True, False]),
            new_prod=random.choice([True, False]),
            dotd=random.choice([True, False]),
            best_sellers=random.choice([True, False])
        )

        image_file = create_dummy_image()
        secondary_image_file = create_dummy_image()

        product.image.save(image_file.name, image_file, save=False)
        product.secondary_image.save(secondary_image_file.name, secondary_image_file, save=False)

        product.save()
    print(f"{count} fake products added successfully.")

add_fake_products(100)