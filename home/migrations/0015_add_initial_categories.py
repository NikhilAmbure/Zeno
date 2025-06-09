from django.db import migrations

def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    SubCategory = apps.get_model('home', 'SubCategory')

    # Create main categories
    electronics = Category.objects.create(name='Electronics')
    clothes = Category.objects.create(name='Clothes')
    jewelry = Category.objects.create(name='Jewelry')
    perfume = Category.objects.create(name='Perfume')
    cosmetics = Category.objects.create(name='Cosmetics')
    bags = Category.objects.create(name='Bags')

    # Create subcategories for Electronics
    electronics_subs = [
        ('Phones', 'phones'),
        ('Laptops', 'laptops'),
        ('Tablets', 'tablets'),
        ('Smartwatches', 'smartwatches'),
        ('Headphones', 'headphones')
    ]
    for name, slug in electronics_subs:
        SubCategory.objects.create(category=electronics, name=name, slug=slug)

    # Create subcategories for Clothes
    clothes_subs = [
        ('T-shirts', 't-shirts'),
        ('Pants', 'pants'),
        ('Dresses', 'dresses'),
        ('Jackets', 'jackets'),
        ('Shorts & Jeans', 'shorts-jeans')
    ]
    for name, slug in clothes_subs:
        SubCategory.objects.create(category=clothes, name=name, slug=slug)

    # Create subcategories for Jewelry
    jewelry_subs = [
        ('Necklaces', 'necklaces'),
        ('Rings', 'rings'),
        ('Earrings', 'earrings'),
        ('Bracelets', 'bracelets')
    ]
    for name, slug in jewelry_subs:
        SubCategory.objects.create(category=jewelry, name=name, slug=slug)

    # Create subcategories for Perfume
    perfume_subs = [
        ('Men\'s Perfume', 'mens-perfume'),
        ('Women\'s Perfume', 'womens-perfume'),
        ('Unisex Perfume', 'unisex-perfume')
    ]
    for name, slug in perfume_subs:
        SubCategory.objects.create(category=perfume, name=name, slug=slug)

    # Create subcategories for Cosmetics
    cosmetics_subs = [
        ('Makeup', 'makeup'),
        ('Skincare', 'skincare'),
        ('Haircare', 'haircare'),
        ('Nailcare', 'nailcare')
    ]
    for name, slug in cosmetics_subs:
        SubCategory.objects.create(category=cosmetics, name=name, slug=slug)

    # Create subcategories for Bags
    bags_subs = [
        ('Handbags', 'handbags'),
        ('Backpacks', 'backpacks'),
        ('Wallets', 'wallets'),
        ('Travel Bags', 'travel-bags')
    ]
    for name, slug in bags_subs:
        SubCategory.objects.create(category=bags, name=name, slug=slug)

def remove_categories(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_subcategory_slug'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, remove_categories),
    ] 