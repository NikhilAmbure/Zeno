# home/management/commands/migrate_to_cloudinary.py
# Create this file to migrate existing images

from django.core.management.base import BaseCommand
from home.models import Product  # Adjust import based on your model
import cloudinary.uploader

class Command(BaseCommand):
    help = 'Migrate existing images to Cloudinary'

    def handle(self, *args, **options):
        products = Product.objects.filter(image__isnull=False)
        
        for product in products:
            if product.image:
                try:
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
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to migrate image for {product.name}: {str(e)}')
                    )

# Run with: python manage.py migrate_to_cloudinary