from django.test import TestCase, Client
from django.urls import reverse
from .models import Verse, VerseLine
from django.contrib.auth.models import User

# Create your tests here.

class VerseSlugTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Create a test verse
        self.verse = Verse.objects.create(
            title='Test Verse',
            content='Line 1\nLine 2'
        )

    def test_slug_generation(self):
        """Test that slugs are generated correctly from titles"""
        self.assertEqual(self.verse.slug, 'test-verse')

        # Test duplicate title handling
        verse2 = Verse.objects.create(
            title='Test Verse',
            content='Different content'
        )
        self.assertEqual(verse2.slug, 'test-verse-1')

        # Test special characters
        verse3 = Verse.objects.create(
            title='Test! @#$% Verse',
            content='Special characters'
        )
        self.assertEqual(verse3.slug, 'test-verse-2')

    def test_urls_use_slug(self):
        """Test that URLs use slugs instead of IDs"""
        # Test detail view
        response = self.client.get(reverse('versus:detail', kwargs={'slug': self.verse.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.verse.title)

        # Test edit view
        response = self.client.get(reverse('versus:edit', kwargs={'slug': self.verse.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.verse.title)

    def test_create_verse_generates_slug(self):
        """Test that creating a verse through the view generates a slug"""
        data = {
            'title': 'New Test Verse',
            'line_1': 'First line',
            'grade_1': '50'
        }
        response = self.client.post(reverse('versus:create'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that the verse was created with correct slug
        verse = Verse.objects.get(title='New Test Verse')
        self.assertEqual(verse.slug, 'new-test-verse')
        self.assertRedirects(response, reverse('versus:detail', kwargs={'slug': 'new-test-verse'}))

    def test_edit_verse_maintains_slug(self):
        """Test that editing a verse maintains its slug"""
        data = {
            'title': 'Updated Test Verse',
            'line_1': 'Updated line',
            'grade_1': '50'
        }
        original_slug = self.verse.slug
        response = self.client.post(
            reverse('versus:edit', kwargs={'slug': original_slug}),
            data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Refresh verse from database
        self.verse.refresh_from_db()
        self.assertEqual(self.verse.title, 'Updated Test Verse')
        self.assertEqual(self.verse.slug, original_slug)  # Slug should not change

    def test_invalid_slug_returns_404(self):
        """Test that invalid slugs return 404"""
        response = self.client.get(reverse('versus:detail', kwargs={'slug': 'non-existent-verse'}))
        self.assertEqual(response.status_code, 404)

    def test_special_characters_in_title(self):
        """Test handling of special characters in title for slug generation"""
        special_titles = [
            ('Hello! World', 'hello-world'),
            ('Test & Test', 'test-test'),
            ('Multiple   Spaces', 'multiple-spaces'),
            ('Über Café', 'uber-cafe'),
            ('123 Numbers', '123-numbers'),
            ('!@#$%^&*()', ''),  # Should generate a slug with just the timestamp
        ]

        for title, expected_base in special_titles:
            verse = Verse.objects.create(title=title, content='Test content')
            if expected_base:
                self.assertTrue(verse.slug.startswith(expected_base))
            self.assertTrue(len(verse.slug) > 0)  # Ensure a slug was generated
