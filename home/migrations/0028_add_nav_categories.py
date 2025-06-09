from django.db import migrations

def add_nav_categories(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    SubCategory = apps.get_model('home', 'SubCategory')

    # Create main categories
    electronics = Category.objects.get_or_create(name='Electronics')[0]
    mens = Category.objects.get_or_create(name='Men\'s')[0]
    womens = Category.objects.get_or_create(name='Women\'s')[0]
    jewelry = Category.objects.get_or_create(name='Jewelry')[0]
    perfume = Category.objects.get_or_create(name='Perfume')[0]

    # Define all subcategories
    categories_data = [
        (electronics, [
            ('Desktop', 'desktop'),
            ('Laptop', 'laptop'),
            ('Camera', 'camera'),
            ('Tablet', 'tablet'),
            ('Headphone', 'headphone'),
            ('Smart Watch', 'smart-watch'),
            ('Smart TV', 'smart-tv'),
            ('Keyboard', 'keyboard'),
            ('Mouse', 'mouse'),
            ('Microphone', 'microphone'),
        ]),
        (mens, [
            ('Formal', 'formal-men'),
            ('Casual', 'casual-men'),
            ('Sports', 'sports-men'),
            ('Jacket', 'jacket-men'),
            ('Sunglasses', 'sunglasses'),
            ('Shirt', 'shirt'),
            ('Shorts & Jeans', 'shorts-jeans'),
            ('Safety Shoes', 'safety-shoes'),
            ('Wallet', 'wallet'),
        ]),
        (womens, [
            ('Formal', 'formal-women'),
            ('Casual', 'casual-women'),
            ('Perfume', 'perfume-women'),
            ('Cosmetics', 'cosmetics'),
            ('Bags', 'bags'),
            ('Dress & Frock', 'dress-frock'),
            ('Earrings', 'earrings-women'),
            ('Necklace', 'necklace-women'),
            ('Makeup Kit', 'makeup-kit'),
        ]),
        (jewelry, [
            ('Earrings', 'earrings'),
            ('Couple Rings', 'couple-rings'),
            ('Necklace', 'necklace'),
            ('Bracelets', 'bracelets'),
        ]),
        (perfume, [
            ('Clothes Perfume', 'clothes-perfume'),
            ('Deodorant', 'deodorant'),
            ('Flower Fragrance', 'flower-fragrance'),
            ('Air Freshener', 'air-freshener'),
        ]),
    ]

    # Create all subcategories
    for category, subcats in categories_data:
        for name, slug in subcats:
            SubCategory.objects.get_or_create(
                category=category,
                name=name,
                defaults={'slug': slug}
            )

def remove_nav_categories(apps, schema_editor):
    # We don't need to implement reverse migration as it might affect existing data
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_merge_20250609_2152'),
    ]

    operations = [
        migrations.RunPython(add_nav_categories, remove_nav_categories),
    ] 