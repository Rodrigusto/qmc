from django.views.generic import ListView, View, TemplateView

# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

# from django.utils.decorators import method_decorator
import datetime

from .models import Sale, Customer, Neighborhood, SalesChannel
from .forms import SaleForm, SaleItemFormSet
from .services import create_sale, cancel_sale, get_monthly_summary
from core.mixins import LoginRequiredMixin


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales/list.html"
    context_object_name = "sales"

    def get_queryset(self):
        return (
            Sale.objects.select_related("customer", "channel", "neighborhood")
            .prefetch_related("items__product")
            .order_by("-date", "-created_at")
        )


class SaleCreateView(LoginRequiredMixin, View):
    """
    View complexa — cabeçalho da venda (SaleForm) +
    itens dinâmicos (SaleItemFormSet) processados juntos.
    """

    template_name = "sales/new.html"

    def get_context(self, form=None, formset=None):
        return {
            "form": form or SaleForm(initial={"date": datetime.date.today()}),
            "formset": formset or SaleItemFormSet(prefix="items"),
        }

    def get(self, request):
        return self._render(request)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST, prefix="items")

        if form.is_valid() and formset.is_valid():
            return self._process(request, form, formset)

        messages.error(request, "Corrija os erros abaixo.")
        return self._render(request, form, formset)

    def _process(self, request, form, formset):
        items = [
            {
                "product_id": f.cleaned_data["product"].pk,
                "quantity": f.cleaned_data["quantity"],
                "unit_price": f.cleaned_data["unit_price"],
            }
            for f in formset
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]

        if not items:
            messages.error(request, "Adicione ao menos um produto.")
            return self._render(request, form, formset)

        try:
            sale = create_sale(form.cleaned_data, items)
            messages.success(request, f"Venda registrada! Total: R$ {sale.total:.2f}")
            return redirect("sales:list")
        except Exception as e:
            messages.error(request, f"Erro ao registrar venda: {e}")
            return self._render(request, form, formset)

    def _render(self, request, form=None, formset=None):
        from django.shortcuts import render

        return render(request, self.template_name, self.get_context(form, formset))


class SaleCancelView(LoginRequiredMixin, View):
    """Só aceita POST — cancela venda e estorna estoque."""

    def post(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        try:
            cancel_sale(sale)
            messages.success(request, "Venda cancelada e estoque estornado.")
        except Exception as e:
            messages.error(request, f"Erro ao cancelar: {e}")
        return redirect("sales:list")


class SaleSummaryView(LoginRequiredMixin, TemplateView):
    template_name = "sales/summary.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = datetime.date.today()
        month = int(self.request.GET.get("month", now.month))
        year = int(self.request.GET.get("year", now.year))
        ctx.update(
            {
                "data": get_monthly_summary(month, year),
                "month": month,
                "year": year,
                "months": [
                    (i, datetime.date(2000, i, 1).strftime("%B")) for i in range(1, 13)
                ],
            }
        )
        return ctx


class CustomerListView(LoginRequiredMixin, View):
    template_name = "sales/customers.html"

    def get(self, request):
        from django.shortcuts import render

        return render(
            request, self.template_name, {"customers": Customer.objects.all()}
        )

    def post(self, request):
        action = request.POST.get("action")
        try:
            if action == "create":
                Customer.objects.create(
                    name=request.POST["name"],
                    phone=request.POST.get("phone", ""),
                    note=request.POST.get("note", ""),
                )
                messages.success(request, "Cliente cadastrado!")
            elif action == "toggle":
                c = get_object_or_404(Customer, pk=request.POST["pk"])
                c.is_active = not c.is_active
                c.save()
                messages.success(
                    request, f'Cliente {"ativado" if c.is_active else "desativado"}.'
                )
        except Exception as e:
            messages.error(request, f"Erro: {e}")
        return redirect("sales:customers")


class NeighborhoodListView(LoginRequiredMixin, View):
    template_name = "sales/neighborhoods.html"

    def get(self, request):
        from django.shortcuts import render

        return render(
            request, self.template_name, {"neighborhoods": Neighborhood.objects.all()}
        )

    def post(self, request):
        action = request.POST.get("action")
        try:
            if action == "create":
                Neighborhood.objects.create(
                    name=request.POST["name"],
                    delivery_fee=request.POST.get("delivery_fee", 0),
                )
                messages.success(request, "Bairro cadastrado!")
            elif action == "toggle":
                n = get_object_or_404(Neighborhood, pk=request.POST["pk"])
                n.is_active = not n.is_active
                n.save()
                messages.success(request, "Bairro atualizado.")
        except Exception as e:
            messages.error(request, f"Erro: {e}")
        return redirect("sales:neighborhoods")


class ChannelListView(LoginRequiredMixin, View):
    template_name = "sales/channels.html"

    def get(self, request):
        from django.shortcuts import render

        return render(
            request, self.template_name, {"channels": SalesChannel.objects.all()}
        )

    def post(self, request):
        action = request.POST.get("action")
        try:
            if action == "create":
                SalesChannel.objects.create(
                    name=request.POST["name"],
                    fee_type=request.POST.get("fee_type", "none"),
                    fee_value=request.POST.get("fee_value", 0),
                )
                messages.success(request, "Canal cadastrado!")
            elif action == "toggle":
                c = get_object_or_404(SalesChannel, pk=request.POST["pk"])
                c.is_active = not c.is_active
                c.save()
                messages.success(request, "Canal atualizado.")
        except Exception as e:
            messages.error(request, f"Erro: {e}")
        return redirect("sales:channels")
