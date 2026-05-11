from django.views.generic import ListView, View
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
import datetime

from .models import Purchase, Stock, Supplier
from .forms import PurchaseForm, PurchaseItemFormSet
from .services import create_purchase, cancel_purchase
# from ingredients.models import Ingredient
from core.mixins import LoginRequiredMixin


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "purchases/list.html"
    context_object_name = "purchases"

    def get_queryset(self):
        return (
            Purchase.objects.filter(is_active=True)
            .select_related("supplier")
            .prefetch_related("items__ingredient")
        )


class PurchaseCreateView(LoginRequiredMixin, View):
    template_name = "purchases/new.html"

    def get_context(self, form=None, formset=None):
        return {
            "form": form or PurchaseForm(initial={"date": datetime.date.today()}),
            "formset": formset or PurchaseItemFormSet(prefix="items"),
        }

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    def post(self, request):
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST, prefix="items")

        if form.is_valid() and formset.is_valid():
            return self._process(request, form, formset)

        messages.error(request, "Corrija os erros abaixo.")
        return render(request, self.template_name, self.get_context(form, formset))

    def _process(self, request, form, formset):
        items = [
            {
                "ingredient_id": f.cleaned_data["ingredient"].pk,
                "quantity": f.cleaned_data["quantity"],
                "total_price": f.cleaned_data["total_price"],
            }
            for f in formset
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]

        if not items:
            messages.error(request, "Adicione ao menos um item.")
            return render(request, self.template_name, self.get_context(form, formset))

        try:
            create_purchase(
                supplier_id=form.cleaned_data["supplier"].pk,
                date=form.cleaned_data["date"],
                note=form.cleaned_data.get("note", ""),
                items=items,
            )
            messages.success(request, "Compra registrada e estoque atualizado!")
            return redirect("purchases:list")
        except Exception as e:
            messages.error(request, f"Erro ao registrar compra: {e}")
            return render(request, self.template_name, self.get_context(form, formset))


class PurchaseCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk, is_active=True)
        try:
            cancel_purchase(purchase)
            messages.success(request, "Compra cancelada e estoque estornado.")
        except Exception as e:
            messages.error(request, f"Erro ao cancelar: {e}")
        return redirect("purchases:list")


class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = "purchases/stock.html"
    context_object_name = "stocks"

    def get_queryset(self):
        return Stock.objects.select_related("ingredient").order_by("ingredient__name")


class SupplierListView(LoginRequiredMixin, View):
    template_name = "purchases/suppliers.html"

    def get(self, request):
        return render(
            request, self.template_name, {"suppliers": Supplier.objects.all()}
        )

    def post(self, request):
        action = request.POST.get("action")
        try:
            if action == "create":
                Supplier.objects.create(
                    name=request.POST["name"],
                    phone=request.POST.get("phone", ""),
                    email=request.POST.get("email", ""),
                    note=request.POST.get("note", ""),
                )
                messages.success(request, "Fornecedor cadastrado!")
            elif action == "toggle":
                s = get_object_or_404(Supplier, pk=request.POST["pk"])
                s.is_active = not s.is_active
                s.save()
                messages.success(
                    request, f'Fornecedor {"ativado" if s.is_active else "desativado"}.'
                )
        except Exception as e:
            messages.error(request, f"Erro: {e}")
        return redirect("purchases:suppliers")
