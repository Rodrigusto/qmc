from django import forms
from .models import Sale, Customer, Neighborhood, SalesChannel  # , SaleItem
from products.models import Product


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = (
            "date",
            "channel",
            "customer",
            "neighborhood",
            "status",
            "discount",
            "note",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.TextInput(),
            "discount": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # só ativos nos selects
        self.fields["channel"].queryset = SalesChannel.objects.filter(is_active=True)
        self.fields["customer"].queryset = Customer.objects.filter(is_active=True)
        self.fields["neighborhood"].queryset = Neighborhood.objects.filter(
            is_active=True
        )
        self.fields["customer"].required = False
        self.fields["neighborhood"].required = False
        self.fields["discount"].required = False


class SaleItemForm(forms.Form):
    """Form para um único item da venda — usado em formset."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True), empty_label="Selecione..."
    )
    quantity = forms.IntegerField(min_value=1, initial=1)
    unit_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)


# Formset — permite múltiplos SaleItemForm no mesmo POST
SaleItemFormSet = forms.formset_factory(
    SaleItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
)
