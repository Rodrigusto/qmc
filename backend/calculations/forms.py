from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import FixedCost, Expense


class FixedCostForm(forms.ModelForm):
    class Meta:
        model  = FixedCost
        fields = ('name', 'category', 'monthly_amount')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag    = False  # HTMX cuida do form tag
        self.helper.form_class  = ''
        self.helper.layout = Layout(
            Row(
                Column(Field('name',           placeholder='Ex: Aluguel do ponto'), css_class='form-group col-md-5'),
                Column(Field('category'),                                            css_class='form-group col-md-3'),
                Column(Field('monthly_amount', placeholder='0,00'),                 css_class='form-group col-md-3'),
            ),
        )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        fields = ('name', 'amount', 'date', 'note')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.TextInput(attrs={'placeholder': 'Observação opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag   = False
        self.helper.form_class = ''
        self.helper.layout = Layout(
            Row(
                Column(Field('name',   placeholder='Ex: Conserto geladeira'), css_class='form-group col-md-4'),
                Column(Field('amount', placeholder='0,00'),                   css_class='form-group col-md-2'),
                Column(Field('date'),                                          css_class='form-group col-md-2'),
                Column(Field('note'),                                          css_class='form-group col-md-4'),
            ),
        )