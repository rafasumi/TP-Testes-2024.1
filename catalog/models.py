import uuid

from datetime import date
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse


class User(AbstractUser):
    @property
    def can_borrow_book(self):
        if self.bookinstance_set.count() >= 3:
            return False
        
        if self.bookinstance_set.filter(due_back__lt=date.today()).count() > 1:
            return False

        return True

class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Insira um gênero literário'
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('genre', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message='Gênero já existe'
            ),
        ]


class Book(models.Model):
    title = models.CharField('Título', max_length=200)
    author = models.ForeignKey('Author', verbose_name='Autor', on_delete=models.RESTRICT, null=True)
    summary = models.TextField('Sumário',
        max_length=1000, help_text='Insira uma descrição do livro')
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='<a href="https://www.isbn-international.org/content/what-isbn'
                                      '">Número ISBN</a>')
    genre = models.ManyToManyField('Genre', verbose_name='Gênero', help_text='Selecione os gêneros')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="ID desse livro na biblioteca")
    book = models.ForeignKey('Book', verbose_name='Livro', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField('Versão', max_length=200)
    due_back = models.DateField('Prazo de devolução', null=True, blank=True)
    language = models.ForeignKey(
        'Language', on_delete=models.RESTRICT, verbose_name='Idioma', null=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


    LOAN_STATUS = (
        ('m', 'Em manutenção'),
        ('o', 'Emprestado'),
        ('a', 'Disponível'),
        ('r', 'Reservado'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id} ({self.book.title})'
    
    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)



class Author(models.Model):
    first_name = models.CharField('Primeiro nome', max_length=100)
    last_name = models.CharField('Último nome', max_length=100)
    date_of_birth = models.DateField('Data de nascimento', null=True, blank=True)
    date_of_death = models.DateField('Data de morte', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


class Language(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Insira uma linguagem'
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('language', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message='Linguagem já existe'
            ),
        ]
