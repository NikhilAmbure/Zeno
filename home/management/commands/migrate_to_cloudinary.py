# home/management/commands/migrate_to_cloudinary.py
from django.core.management.base import BaseCommand
from home.models import Product  # Adjust import based on your model
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = 'Migrate existing images to Cloudinary'
    
    def handle(self, *args, **options):
        products = Product.objects.filter(image__isnull=False)
        
        for product in products:
            if product.image:
                try:
                    # Check if image is already a Cloudinary URL/resource
                    image_str = str(product.image)
                    
                    # Skip if already migrated to Cloudinary
                    if 'cloudinary.com' in image_str or not hasattr(product.image, 'path'):
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {product.name} - already on Cloudinary or no local path')
                        )
                        continue
                    
                    # Check if local file exists
                    if not os.path.exists(product.image.path):
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {product.name} - local file not found: {product.image.path}')
                        )
                        continue
                    
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        product.image.path,
                        folder="products/",  # Optional: organize in folders
                        public_id=f"product_{product.id}"
                    )
                    
                    # Update the image field with Cloudinary URL
                    product.image = result['public_id']
                    product.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully migrated image for {product.name}')
                    )
                    
                except AttributeError as e:
                    if "'CloudinaryResource' object has no attribute 'path'" in str(e):
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {product.name} - already a CloudinaryResource')
                        )
                        continue
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'AttributeError for {product.name}: {str(e)}')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to migrate image for {product.name}: {str(e)}')
                    )

# Run with: python manage.py migrate_to_cloudinary