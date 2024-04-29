from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse

import uuid


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
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(
        max_length=1000, help_text='Insira uma descrição do livro')
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='<a href="https://www.isbn-international.org/content/what-isbn'
                                      '">Número ISBN</a>')
    genre = models.ManyToManyField('Genre', help_text='Selecione os gêneros')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="ID desse livro na biblioteca")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    language = models.ForeignKey(
        'Language', on_delete=models.RESTRICT, null=True)

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

    def __str__(self):
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Morreu', null=True, blank=True)

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
