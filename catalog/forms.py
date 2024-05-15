import datetime
from typing import Any

from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from catalog.models import BookInstance


def clean_due_back_helper(due_back):
    if due_back < datetime.date.today():
        raise ValidationError(_('Data inválida - nova data já passou'))

    if due_back > datetime.date.today() + datetime.timedelta(weeks=4):
        raise ValidationError(
            _('Data inválida - nova data é daqui a mais de 4 semanas'))

    return due_back


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        return clean_due_back_helper(self.cleaned_data['due_back'])

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Novo prazo')}
        help_texts = {'due_back': _(
            'Insira uma data entre hoje e daqui 4 semanas.')}


class BorrowBookModelForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_due_back(self):
        return clean_due_back_helper(self.cleaned_data['due_back'])
    def clean(self) -> dict[str, Any]:
        if self.instance.status != 'a':
            raise ValidationError(_('Esta cópia está indisponível'))

        if not self.user.can_borrow_book:
            raise ValidationError(
                _('Você não pode pegar livros emprestados se tiver algum livro atrasado ou se já tiver pego 3 livros')
            )

        return super().clean()

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Prazo desejado')}
        help_texts = {'due_back': _(
            'Insira uma data entre hoje e daqui 4 semanas.')}

class ReturnBookModelForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        if self.instance.status != 'o':
            raise ValidationError(_('Esta cópia não pode ser devolvida. Ela não está emprestada.'))
        return super().clean()

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Prazo desejado')}
