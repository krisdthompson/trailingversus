from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import re

def count_syllables(word):
    """
    A simple syllable counter for English text.
    This is a basic implementation and may not be 100% accurate for all cases.
    """
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if not word:
        return 0
        
    # Count groups of vowels (including 'y')
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    
    # Handle silent e
    if word.endswith('e'):
        count -= 1
    
    # Handle special cases
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        count += 1
        
    return max(1, count)  # Every word has at least one syllable

class Poem(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('poems:detail', args=[str(self.id)])
    
    def get_edit_url(self):
        return reverse('poems:edit', args=[str(self.id)])

    def save(self, *args, **kwargs):
        self.syllable_count = count_syllables(self.content)
        super().save(*args, **kwargs)

class PoemLine(models.Model):
    poem = models.ForeignKey(Poem, related_name='lines', on_delete=models.CASCADE)
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
        unique_together = ['poem', 'position']

    def save(self, *args, **kwargs):
        if not hasattr(self, '_skip_syllable_count') or not self._skip_syllable_count:
            # Only calculate syllables if not manually overridden
            words = self.content.split()
            self.syllable_count = sum(count_syllables(word) for word in words)
            self.is_syllable_override = False
        if hasattr(self, '_skip_syllable_count'):
            delattr(self, '_skip_syllable_count')
            self.is_syllable_override = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.poem.title} - Line {self.position}"
