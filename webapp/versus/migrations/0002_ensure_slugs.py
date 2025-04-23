from django.db import migrations
from django.utils.text import slugify
from django.utils import timezone

def generate_slugs(apps, schema_editor):
    Verse = apps.get_model('versus', 'Verse')
    for verse in Verse.objects.filter(slug=''):
        base_slug = slugify(verse.title)
        if not base_slug:
            base_slug = f"verse-{timezone.now().strftime('%Y%m%d-%H%M%S')}"
        
        slug = base_slug
        n = 1
        while Verse.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{n}"
            n += 1
        verse.slug = slug
        verse.save()

class Migration(migrations.Migration):
    dependencies = [
        ('versus', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_slugs, reverse_code=migrations.RunPython.noop),
    ] 