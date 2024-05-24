from django.test import TestCase

from catalog.models import Author, Genre, Book, BookInstance, User
import datetime
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate

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

class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user_data = {
            'username': 'testuser',
            'password': 'secret123',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }

        User.objects.create_user(**user_data)

    def test_can_borrow_book(self):
        user  = User.objects.get(id=1)
        self.assertEqual(user.can_borrow_book, True)

        
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

    def test_title_is_not_null(self):
        book = Book.objects.get(id=1)
        self.assertIsNotNone(book.title)

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

        User = get_user_model()
        user_data = {
            'username': 'testuser',
            'password': 'secret123',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }

        User.objects.create_user(**user_data)

    def test_can_borrow_book_limit(self):
        return_date = timezone.localtime() + datetime.timedelta(days=4)
        user  = User.objects.get(id=1)
        test_book = Book.objects.get(id=1)
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        self.assertEqual(user.can_borrow_book, True)

    def test_can_not_borrow_book_limit(self):
        return_date = timezone.localtime() + datetime.timedelta(days=4)
        user  = User.objects.get(id=1)
        test_book = Book.objects.get(id=1)
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        self.assertEqual(user.can_borrow_book, False)

    def test_can_borrow_book_due_back(self):
        return_date = timezone.localtime() + datetime.timedelta(days=4)
        user  = User.objects.get(id=1)
        test_book = Book.objects.get(id=1)
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        self.assertEqual(user.can_borrow_book, True)

    def test_can_not_borrow_book_due_back(self):
        return_date = timezone.localtime() - datetime.timedelta(days=1)
        user  = User.objects.get(id=1)
        test_book = Book.objects.get(id=1)
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=user, status='r')
        self.assertEqual(user.can_borrow_book, False)


class UserCreationTest(TestCase):
    def test_create_valid_user(self):
        User = get_user_model()
        user_data = {
            'username': 'testuser',
            'password': 'secret123',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }

        user = User.objects.create_user(**user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(check_password('secret123', user.password))
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_create_invalid_user(self):
        User = get_user_model()
        user_data = {
            'username': 'testuser~~',
            'password': 'secret123',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }

        user = User.objects.create_user(**user_data)
        
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_with_invalid_email(self):
        User = get_user_model()
        user_data = {
            'username': 'testuser',
            'password': 'secret123',
            'email': 'invalidemail',  # Email inválido só pra testar em
            'first_name': 'John',
            'last_name': 'Doe',
        }

        user = User(**user_data)

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_with_duplicate_username(self):
        User = get_user_model()
        User.objects.create_user(username='testuser1', password='secret123', email='test@example.com')

        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='testuser1', password='anotherpassword', email='another@example.com')

class UserAuthenticationTest(TestCase):
    def test_user_authentication_with_valid_credentials(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='secret123', email='test@example.com')

        authenticated_user = authenticate(username='testuser', password='secret123')
        self.assertEqual(authenticated_user, user)

    def test_user_authentication_with_invalid_username(self):
        User = get_user_model()
        User.objects.create_user(username='testuser', password='secret123', email='test@example.com')

        authenticated_user = authenticate(username='nonexistentuser', password='secret123')
        self.assertIsNone(authenticated_user)

    def test_user_authentication_with_invalid_password(self):
        User = get_user_model()
        User.objects.create_user(username='testuser', password='secret123', email='test@example.com')

        authenticated_user = authenticate(username='testuser', password='wrongpassword')
        self.assertIsNone(authenticated_user)

    def test_user_password_hashing(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='secret123', email='test@example.com')

        stored_password_hash = user.password
        is_password_correct = check_password('secret123', stored_password_hash)
        self.assertTrue(is_password_correct)

class GenreUniqueConstraintTest(TestCase):
    def test_create_duplicate_genre_name(self):
        Genre.objects.create(name='Fantasy')
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name='Fantasy')



