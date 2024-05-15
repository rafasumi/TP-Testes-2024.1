import datetime
from datetime import timedelta
import random

from django.test import TestCase
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from catalog.forms import RenewBookModelForm
from catalog.forms import BorrowBookModelForm
from catalog.forms import ReturnBookModelForm
from catalog.models import User, BookInstance, Book, Author, Language, Genre

class RenewBookModelFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookModelForm()
        self.assertTrue(form.fields['due_back'].label is None or form.fields['due_back'].label == 'Novo prazo')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookModelForm()
        self.assertEqual(form.fields['due_back'].help_text, 'Insira uma data entre hoje e daqui 4 semanas.')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())


class BorrowBookModelFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.language = Language.objects.create(name="English")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(title="Sample Book", author=self.author)
        self.genre = Genre.objects.create(name="Fiction")
        self.book.genre.add(self.genre)
        self.book_instance = BookInstance.objects.create(
            book=self.book, imprint="Imprint", language=self.language,
            borrower=self.user, status='a', due_back=timezone.now() + timedelta(days=20))

    def test_instance_not_available(self):
        self.book_instance.status = 'b'
        self.book_instance.save()
        form = BorrowBookModelForm(user=self.user, data={'due_back': timezone.now()}, instance=self.book_instance)
        self.assertFalse(form.is_valid())
        self.assertIn(_('Esta cópia está indisponível'), form.errors['__all__'])

    def test_user_cannot_borrow_due_to_three_books(self):
        for _ in range(2):
            BookInstance.objects.create(book=self.book, imprint="Imprint", language=self.language, borrower=self.user, status='a', due_back=timezone.now() + timedelta(days=20))
        
        form = BorrowBookModelForm(user=self.user, data={'due_back': timezone.now()}, instance=self.book_instance)
        self.assertFalse(form.is_valid())
        self.assertIn('Você não pode pegar livros emprestados se tiver algum livro atrasado ou se já tiver pego 3 livros', form.errors.get('__all__', []))

class ReturnBookModelFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secret')
        self.borrowed_book_instance = BookInstance.objects.create(
            borrower=self.user, status='o', due_back=timezone.now() + timedelta(days=10))
        
        if hasattr(self.user, 'borrowed_books'):
            self.user.borrowed_books.add(self.borrowed_book_instance)
    
    def clear_test_data(self):
        for model in (User, Book, BookInstance):
            model.objects.all().delete()

    def test_invalid_book_status(self):
        invalid_book_instance = BookInstance.objects.create(status='m')
        form = ReturnBookModelForm(user=self.user, instance=invalid_book_instance)
        self.assertFalse(form.is_valid(), "Form should be invalid for book with status != 'o'")

    def test_cannot_change_book_status(self):
        form = ReturnBookModelForm(user=self.user, instance=self.borrowed_book_instance)
        form.instance.status = 'm'
        self.assertFalse(form.is_valid(), "Form should not allow changing book status")

    def test_user_without_permission(self):
        permissionless_user = User.objects.create(username="nopermission")
        form = ReturnBookModelForm(user=permissionless_user, instance=self.borrowed_book_instance)
        self.assertFalse(form.is_valid(), "Form should be invalid for user without permission")

    class BorrowBookModelFormTest(TestCase):
        
        def test_user_with_reached_limit(self):
            author = Author.objects.create(first_name="Test", last_name="Author")
            book = Book.objects.create(title="Test Book", author=author)
            user = User.objects.create_user(username='testuser', password='secret')
            for _ in range(3):
                BookInstance.objects.create(book=book, borrower=user, status='o')

            form = BorrowBookModelForm(user=user)

            self.assertFalse(form.is_valid(), "Form should be invalid for user with reached limit")
            expected_message = ('Você não pode pegar livros emprestados se tiver algum livro atrasado ou se já tiver pego 3 livros')
            self.assertEqual(list(form.non_field_errors())[0], expected_message)

        def test_user_can_borrow(self):
            author = Author.objects.create(first_name="Test", last_name="Author")
            book = Book.objects.create(title="Test Book", author=author)
            user = User.objects.create_user(username='testuser', password='secret')
            form = BorrowBookModelForm(user=user)

            self.assertTrue(form.is_valid(), "Form should be valid for user under limit")
