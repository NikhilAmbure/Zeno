# Generated migration file for uploading existing images to Cloudinary
# Place this file in your app's migrations folder (e.g., home/migrations/0002_migrate_images_to_cloudinary.py)

from django.db import migrations
import cloudinary.uploader
import os
from django.conf import settings

def upload_existing_images_to_cloudinary(apps, schema_editor):
    """
    Upload all existing product images to Cloudinary
    """
    # Get the Product model
    Product = apps.get_model('home', 'Product')  # Replace 'home' with your actual app name
    
    uploaded_count = 0
    failed_count = 0
    
    print("Starting migration of images to Cloudinary...")
    
    for product in Product.objects.all():
        if product.image:
            try:
                # Get the full path to the image file
                image_path = None
                
                # Try different ways to get the image path
                if hasattr(product.image, 'path'):
                    # If it's a FileField with a local file
                    image_path = product.image.path
                elif hasattr(product.image, 'url'):
                    # If it's already a URL, construct the local path
                    image_name = os.path.basename(product.image.url)
                    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
                
                # Check if file exists
                if image_path and os.path.exists(image_path):
                    print(f"Uploading image for product: {product.name}")
                    
                    # Upload to Cloudinary with a meaningful public_id
                    public_id = f"products/{product.id}_{product.name.replace(' ', '_').lower()}"
                    
                    result = cloudinary.uploader.upload(
                        image_path,
                        public_id=public_id,
                        folder="zeno_products",  # Organize in folders
                        resource_type="image",
                        overwrite=True,
                        transformation=[
                            {'width': 800, 'height': 600, 'crop': 'limit'},
                            {'quality': 'auto'},
                            {'fetch_format': 'auto'}
                        ]
                    )
                    
                    # Update the product with Cloudinary public_id
                    product.image = result['public_id']
                    product.save()
                    
                    uploaded_count += 1
                    print(f"✓ Successfully uploaded: {product.name}")
                    
                else:
                    print(f"✗ Image file not found for product: {product.name}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"✗ Failed to upload image for product {product.name}: {str(e)}")
                failed_count += 1
                continue
    
    print(f"\nMigration completed!")
    print(f"Successfully uploaded: {uploaded_count} images")
    print(f"Failed uploads: {failed_count} images")

def reverse_cloudinary_migration(apps, schema_editor):
    """
    Reverse migration - this is optional and complex
    """
    print("Reverse migration not implemented. Manual cleanup required.")
    pass

class Migration(migrations.Migration):
    
    dependencies = [
        ('home', '0001_initial'),  # Replace with your last migration
    ]
    
    operations = [
        migrations.RunPython(
            upload_existing_images_to_cloudinary,
            reverse_cloudinary_migration
        ),
    ]


# Alternative Migration: If you want to update the model field too
class Migration(migrations.Migration):
    """
    Complete migration that:
    1. Changes ImageField to CloudinaryField
    2. Uploads existing images to Cloudinary
    """
    
    dependencies = [
        ('home', '0001_initial'),  # Replace with your last migration
    ]
    
    operations = [
        # Step 1: Add new CloudinaryField (temporary)
        migrations.AddField(
            model_name='product',
            name='cloudinary_image',
            field=cloudinary.models.CloudinaryField(blank=True, null=True, verbose_name='image'),
        ),
        
        # Step 2: Upload existing images
        migrations.RunPython(
            upload_existing_images_to_cloudinary,
            reverse_cloudinary_migration
        ),
        
        # Step 3: Remove old ImageField
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        
        # Step 4: Rename CloudinaryField to image
        migrations.RenameField(
            model_name='product',
            old_name='cloudinary_image',
            new_name='image',
        ),
    ]


# USAGE INSTRUCTIONS:
"""
1. Update your models.py first:
   
   from cloudinary.models import CloudinaryField
   
   class Product(models.Model):
       name = models.CharField(max_length=200)
       image = CloudinaryField('image', null=True, blank=True)  # Changed from ImageField
       # ... other fields

2. Create the migration file:
   - Create a new file in your app's migrations folder
   - Name it something like: 0002_migrate_images_to_cloudinary.py
   - Copy the migration code above

3. Make sure Cloudinary is configured in settings.py:
   
   import cloudinary
   
   cloudinary.config(
       cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
       api_key=os.getenv('CLOUDINARY_API_KEY'),
       api_secret=os.getenv('CLOUDINARY_API_SECRET'),
       secure=True
   )

4. Run the migration:
   python manage.py migrate

5. The migration will:
   - Find all products with images
   - Upload them to Cloudinary
   - Update the database with Cloudinary public_ids
   - Organize images in a "zeno_products" folder
   - Apply optimizations (resize, quality, format)

6. After successful migration, you can delete the old image files from media folder

TROUBLESHOOTING:
- If migration fails, check your Cloudinary credentials
- Make sure the media files exist in the expected location
- Check Django logs for specific error messages
- You can run the migration multiple times safely (overwrite=True)
"""