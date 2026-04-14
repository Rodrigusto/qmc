from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sale, Customer, Neighborhood, SalesChannel
from .services import create_sale, get_monthly_summary
from products.models import Product
import datetime


def sale_list(request):
    sales = Sale.objects.select_related(
        'customer', 'channel', 'neighborhood'
    ).prefetch_related('items__product')
    return render(request, 'sales/list.html', {'sales': sales})


def sale_new(request):
    products      = Product.objects.filter(is_active=True)
    customers     = Customer.objects.filter(is_active=True)
    neighborhoods = Neighborhood.objects.filter(is_active=True)
    channels      = SalesChannel.objects.filter(is_active=True)
    today         = datetime.date.today().isoformat()

    if request.method == 'POST':
        product_ids  = request.POST.getlist('product_id[]')
        quantities   = request.POST.getlist('quantity[]')
        unit_prices  = request.POST.getlist('unit_price[]')

        items = [
            {'product_id': pid, 'quantity': qty, 'unit_price': price}
            for pid, qty, price in zip(product_ids, quantities, unit_prices)
            if pid and qty and price
        ]

        if not items:
            messages.error(request, 'Adicione ao menos um produto à venda.')
        else:
            neighborhood_id = request.POST.get('neighborhood') or None
            customer_id     = request.POST.get('customer') or None

            data = {
                'date':             request.POST.get('date'),
                'channel_id':       request.POST.get('channel'),
                'customer_id':      customer_id,
                'neighborhood_id':  neighborhood_id,
                'discount':         request.POST.get('discount') or 0,
                'note':             request.POST.get('note', ''),
                'status':           request.POST.get('status'),
            }

            sale = create_sale(data, items)
            messages.success(request, f'Venda registrada! Total: R$ {sale.total:.2f}')
            return redirect('sales:list')

    context = {
        'products':      products,
        'customers':     customers,
        'neighborhoods': neighborhoods,
        'channels':      channels,
        'today':         today,
        'status_choices': Sale.Status.choices,
    }
    return render(request, 'sales/new.html', context)


def sale_summary(request):
    now   = datetime.date.today()
    month = int(request.GET.get('month', now.month))
    year  = int(request.GET.get('year',  now.year))
    data  = get_monthly_summary(month, year)
    months = [(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    return render(request, 'sales/summary.html', {
        'data': data, 'month': month, 'year': year, 'months': months
    })


def sale_cancel(request, pk):
    from .services import cancel_sale
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        try:
            cancel_sale(sale)
            messages.success(request, 'Venda cancelada e estoque estornado.')
        except Exception as e:
            messages.error(request, f'Erro ao cancelar: {e}')
    return redirect('sales:list')


def customer_list(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Customer.objects.create(
                name=request.POST.get('name'),
                phone=request.POST.get('phone', ''),
                note=request.POST.get('note', ''),
            )
            messages.success(request, 'Cliente cadastrado!')

        elif action == 'toggle':
            pk  = request.POST.get('pk')
            cus = get_object_or_404(Customer, pk=pk)
            cus.is_active = not cus.is_active
            cus.save()
            status = 'ativado' if cus.is_active else 'desativado'
            messages.success(request, f'Cliente {status}.')

        return redirect('sales:customers')

    return render(request, 'sales/customers.html', {'customers': customers})


def neighborhood_list(request):
    neighborhoods = Neighborhood.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Neighborhood.objects.create(
                name=request.POST.get('name'),
                delivery_fee=request.POST.get('delivery_fee', 0),
            )
            messages.success(request, 'Bairro cadastrado!')

        elif action == 'toggle':
            pk  = request.POST.get('pk')
            nbh = get_object_or_404(Neighborhood, pk=pk)
            nbh.is_active = not nbh.is_active
            nbh.save()
            messages.success(request, 'Bairro atualizado.')

        return redirect('sales:neighborhoods')

    return render(request, 'sales/neighborhoods.html', {'neighborhoods': neighborhoods})


def channel_list(request):
    channels = SalesChannel.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            SalesChannel.objects.create(
                name=request.POST.get('name'),
                fee_type=request.POST.get('fee_type'),
                fee_value=request.POST.get('fee_value', 0),
            )
            messages.success(request, 'Canal cadastrado!')

        elif action == 'toggle':
            pk  = request.POST.get('pk')
            ch  = get_object_or_404(SalesChannel, pk=pk)
            ch.is_active = not ch.is_active
            ch.save()
            messages.success(request, 'Canal atualizado.')

        return redirect('sales:channels')

    return render(request, 'sales/channels.html', {'channels': channels})