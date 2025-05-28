from home.models import SubCategory
from django.utils.text import slugify

slugs = set()
for sub in SubCategory.objects.all():
    base_slug = slugify(sub.name)
    slug = base_slug
    counter = 1
    while slug in slugs or SubCategory.objects.exclude(id=sub.id).filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    sub.slug = slug
    slugs.add(slug)
    sub.save()

print("Duplicate slugs fixed.")
