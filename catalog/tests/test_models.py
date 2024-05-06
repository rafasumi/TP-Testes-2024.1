from django.test import TestCase

from catalog.models import Author, Genre, Book, BookInstance

import datetime

from django.utils import timezone

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'Primeiro nome')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'Último nome')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'Data de nascimento')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'Data de morte')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')

class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Fantasia')

    def test_genre_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_genre_help_text(self):
        genre = Genre.objects.get(id=1)
        help_text = genre._meta.get_field('name').help_text
        self.assertEqual(help_text, 'Insira um gênero literário')

    #  testar o UniqueConstraint?
        
class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Machado', last_name='de Assis')
        author = Author.objects.get(id=1)

        Genre.objects.create(name='Fantasia')
        Genre.objects.create(name='Ficção Científica')
        genre_objects_for_book = Genre.objects.all()
        
        test_book  = Book.objects.create(title='Dom Casmurro', author=author, summary='Summary Test', isbn='0000000')
        test_book.genre.set(genre_objects_for_book)

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'Título')

    def test_author_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'Autor')

    def test_summary_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'Sumário')

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label,'ISBN')

    def test_genre_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('genre').verbose_name
        self.assertEqual(field_label,'Gênero')

    def test_genre_display(self):
        book = Book.objects.get(id=1)
        self.assertEqual(str(book.display_genre()),'Fantasia, Ficção Científica')

    def test_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(book.get_absolute_url(), '/catalog/book/1')

class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        
        Author.objects.create(first_name='Machado', last_name='de Assis')
        author = Author.objects.get(id=1)

        Genre.objects.create(name='Fantasia')
        Genre.objects.create(name='Ficção Científica')
        genre_objects_for_book = Genre.objects.all()
        
        test_book  = Book.objects.create(title='Dom Casmurro', author=author, summary='Summary Test', isbn='0000000')
        test_book.genre.set(genre_objects_for_book)

        return_date = timezone.localtime() + datetime.timedelta(days=4)

        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower='testuser1', status='r')




