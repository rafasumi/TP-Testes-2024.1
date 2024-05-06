import datetime

from django.test import TestCase
from django.utils import timezone

from catalog.forms import RenewBookModelForm

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