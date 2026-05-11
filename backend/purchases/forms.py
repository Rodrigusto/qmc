from django import forms
from .models import Purchase, Supplier #, PurchaseItem
from ingredients.models import Ingredient


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ("supplier", "date", "note")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Supplier.objects.filter(is_active=True)
        self.fields["note"].required = False


class PurchaseItemForm(forms.Form):
    """Form para um único item da compra — usado em formset."""

    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.filter(is_active=True).order_by("name"),
        empty_label="Selecione...",
    )
    quantity = forms.DecimalField(max_digits=10, decimal_places=3, min_value=0.001)
    total_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


PurchaseItemFormSet = forms.formset_factory(
    PurchaseItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
)
