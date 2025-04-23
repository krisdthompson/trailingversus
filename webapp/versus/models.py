from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import re
from .utils import count_syllables

class Verse(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('versus:detail', kwargs={'slug': self.slug})
    
    def get_edit_url(self):
        return reverse('versus:edit', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a base slug from the title
            base_slug = slugify(self.title)
            
            # If the base slug is empty (title had only special characters),
            # use a timestamp-based slug
            if not base_slug:
                from django.utils import timezone
                base_slug = f"verse-{timezone.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Check if the slug exists and append a number if needed
            slug = base_slug
            n = 1
            while Verse.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug

        # Ensure we always have a slug, even if title changes
        elif not slugify(self.title):
            from django.utils import timezone
            self.slug = f"verse-{timezone.now().strftime('%Y%m%d-%H%M%S')}"

        super().save(*args, **kwargs)

class VerseLine(models.Model):
    verse = models.ForeignKey(Verse, related_name='lines', on_delete=models.CASCADE)
    content = models.TextField()
    position = models.PositiveIntegerField()
    grade = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)
        ],
        default=50
    )
    syllable_count = models.PositiveIntegerField(editable=False)
    is_syllable_override = models.BooleanField(default=False)

    class Meta:
        ordering = ['position']
        unique_together = ['verse', 'position']

    @property
    def calculated_syllables(self):
        """Calculate syllables without using override"""
        words = self.content.split()
        return sum(count_syllables(word) for word in words)

    def save(self, *args, **kwargs):
        if not hasattr(self, '_skip_syllable_count') or not self._skip_syllable_count:
            # Only calculate syllables if not manually overridden
            self.syllable_count = self.calculated_syllables
            self.is_syllable_override = False
        if hasattr(self, '_skip_syllable_count'):
            delattr(self, '_skip_syllable_count')
            self.is_syllable_override = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.verse.title} - Line {self.position}"
