from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import Source, Quote
from django.core.exceptions import ValidationError

class SourceModelTest(TestCase):
    def setUp(self):
        self.movie_source = Source.objects.create(
            name="The Matrix",
            type="MOV"
        )
        self.book_source = Source.objects.create(
            name="1984",
            type="BOOK"
        )

    def test_source_creation(self):
        """Test that source objects are created correctly"""
        self.assertEqual(self.movie_source.name, "The Matrix")
        self.assertEqual(self.movie_source.get_type_display(), "Фильм")
        self.assertEqual(self.book_source.get_type_display(), "Книга")
        self.assertEqual(str(self.movie_source), "Фильм: The Matrix")

    def test_source_unique_name(self):
        """Test that source names must be unique"""
        with self.assertRaises(Exception):
            Source.objects.create(
                name="The Matrix",  # Duplicate name
                type="MOV"
            )


class QuoteModelTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Test Movie",
            type="MOV"
        )

    def test_quote_creation(self):
        """Test that quote objects are created correctly"""
        quote = Quote.objects.create(
            text="This is a test quote",
            source=self.source,
            weight=5
        )
        
        self.assertEqual(quote.text, "This is a test quote")
        self.assertEqual(quote.source, self.source)
        self.assertEqual(quote.weight, 5)
        self.assertEqual(quote.views, 0)
        self.assertEqual(quote.likes, 0)
        self.assertEqual(quote.dislikes, 0)
        self.assertTrue(quote.created_at)

    def test_quote_unique_text(self):
        """Test that quote text must be unique"""
        Quote.objects.create(
            text="Unique quote text",
            source=self.source,
            weight=1
        )
        
        with self.assertRaises(Exception):
            Quote.objects.create(
                text="Unique quote text",  # Duplicate text
                source=self.source,
                weight=2
            )

    def test_quote_clean_method(self):
        """Test the clean method validation"""
        # Create 3 quotes for the same source
        for i in range(3):
            Quote.objects.create(
                text=f"Quote {i}",
                source=self.source,
                weight=1
            )
        
        # Try to create fourth quote - should raise ValidationError
        fourth_quote = Quote(
            text="Fourth quote",
            source=self.source,
            weight=1
        )
        
        with self.assertRaises(ValidationError):
            fourth_quote.clean()

    def test_quote_str_method(self):
        """Test the string representation of quote"""
        quote = Quote.objects.create(
            text="This is a very long quote that should be truncated in the string representation",
            source=self.source,
            weight=1
        )
        
        self.assertIn("This is a very long quote", str(quote))
        self.assertIn("...", str(quote))


class ViewsTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Test Source",
            type="MOV"
        )
        self.quote = Quote.objects.create(
            text="Test quote text",
            source=self.source,
            weight=1
        )

    def test_random_quote_view_without_quotes(self):
        """Test random quote view when no quotes exist"""
        Quote.objects.all().delete()
        
        response = self.client.get(reverse('random_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитаты пока не добавлены")

    def test_random_quote_view_with_quotes(self):
        """Test random quote view when quotes exist"""
        response = self.client.get(reverse('random_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test quote text")
        self.assertContains(response, "Test Source")

    def test_add_quote_view_get(self):
        """Test GET request to add quote form"""
        response = self.client.get(reverse('add_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Добавить новую цитату")
        self.assertContains(response, "form")

    def test_popular_quotes_view(self):
        """Test popular quotes view"""
        response = self.client.get(reverse('popular_quotes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10 самых популярных цитат")

    def test_like_quote_view(self):
        """Test liking a quote"""
        response = self.client.post(
            reverse('like_quote', args=[self.quote.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.likes, 1)

    def test_dislike_quote_view(self):
        """Test disliking a quote"""
        response = self.client.post(
            reverse('dislike_quote', args=[self.quote.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.dislikes, 1)

    def test_next_quote_view(self):
        """Test next quote AJAX view"""
        response = self.client.get(reverse('next_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class FormsTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Existing Source",
            type="MOV"
        )

    def test_quote_form_valid_data(self):
        """Test quote form with valid data"""
        from .forms import QuoteForm
        
        form_data = {
            'text': 'New test quote',
            'source_name': 'New Movie',
            'source_type': 'MOV',
            'weight': '3'
        }
        
        form = QuoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_quote_form_invalid_data(self):
        """Test quote form with invalid data"""
        from .forms import QuoteForm
        
        form_data = {
            'text': '',  # Empty text
            'source_name': 'New Movie',
            'source_type': 'MOV',
            'weight': '0'  # Invalid weight
        }
        
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
        self.assertIn('weight', form.errors)


class WeightSystemTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Weight Test Source",
            type="MOV"
        )
        
        # Create quotes with different weights
        self.low_weight_quote = Quote.objects.create(
            text="Low weight quote",
            source=self.source,
            weight=1
        )
        
        self.high_weight_quote = Quote.objects.create(
            text="High weight quote",
            source=self.source,
            weight=10
        )

    def test_weight_influence(self):
        """Test that higher weight quotes appear more frequently"""
        from .views import get_random_quote
        
        # Test multiple times to see distribution
        results = []
        for _ in range(100):
            quote = get_random_quote()
            if quote:
                results.append(quote.weight)
        
        # High weight quote should appear more often
        high_weight_count = results.count(10)
        low_weight_count = results.count(1)
        
        self.assertGreater(high_weight_count, low_weight_count)


class SessionBehaviorTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Session Test Source",
            type="MOV"
        )
        self.quote = Quote.objects.create(
            text="Session test quote",
            source=self.source,
            weight=1
        )

    def test_like_session_storage(self):
        """Test that likes are stored in session"""
        session = self.client.session
        session['liked_quotes'] = []
        session.save()
        
        response = self.client.post(
            reverse('like_quote', args=[self.quote.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check that quote ID was added to session
        session = self.client.session
        self.assertIn(self.quote.id, session['liked_quotes'])
        
        # Try to like again - should be rejected
        response = self.client.post(
            reverse('like_quote', args=[self.quote.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('уже лайкали', data['message'])