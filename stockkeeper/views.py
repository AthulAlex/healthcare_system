from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Medicine, Prescription
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io
import datetime

def stockkeeper_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'stockkeeper':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@stockkeeper_required
def stock_dashboard(request):
    medicines     = Medicine.objects.all()
    total         = medicines.count()
    low_stock     = medicines.filter(quantity__lt=10)
    today         = datetime.date.today()
    expiring_soon = medicines.filter(
        expiry_date__lte=today + datetime.timedelta(days=30),
        expiry_date__gte=today
    )
    expired = medicines.filter(expiry_date__lt=today)

    context = {
        'total':              total,
        'low_stock_count':    low_stock.count(),
        'expiring_soon_count': expiring_soon.count(),
        'expired_count':      expired.count(),
        'low_stock':          low_stock,
        'expiring_soon':      expiring_soon,
    }
    return render(request, 'stockkeeper/dashboard.html', context)


@stockkeeper_required
def medicine_list(request):
    query     = request.GET.get('q', '')
    medicines = Medicine.objects.all().order_by('name')
    today     = datetime.date.today()
    if query:
        medicines = medicines.filter(name__icontains=query)
    return render(request, 'stockkeeper/medicine_list.html', {
        'medicines': medicines,
        'query':     query,
        'today':     today,
    })


@stockkeeper_required
def add_medicine(request):
    if request.method == 'POST':
        name          = request.POST['name']
        batch_number  = request.POST['batch_number']
        supplier      = request.POST['supplier']
        quantity      = int(request.POST['quantity'])
        minimum_stock = int(request.POST['minimum_stock'])
        expiry_date   = request.POST['expiry_date']

        # Check if medicine already exists
        if Medicine.objects.filter(name__iexact=name, batch_number=batch_number).exists():
            messages.error(request, f"Medicine '{name}' with this batch already exists!")
            return redirect('add_medicine')

        Medicine.objects.create(
            name          = name,
            batch_number  = batch_number,
            supplier      = supplier,
            quantity      = quantity,
            minimum_stock = minimum_stock,
            expiry_date   = expiry_date,
        )
        messages.success(request, f"Medicine '{name}' added successfully!")
        return redirect('medicine_list')

    return render(request, 'stockkeeper/add_medicine.html')


@stockkeeper_required
def update_stock(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        action   = request.POST.get('action', 'set')
        quantity = int(request.POST['quantity'])

        if action == 'add':
            medicine.quantity += quantity
            msg = f"Added {quantity} units to {medicine.name}. New stock: {medicine.quantity}"
        elif action == 'remove':
            if quantity > medicine.quantity:
                messages.error(request, f"Cannot remove {quantity}. Only {medicine.quantity} available.")
                return redirect('update_stock', pk=pk)
            medicine.quantity -= quantity
            msg = f"Removed {quantity} units from {medicine.name}. New stock: {medicine.quantity}"
        else:
            medicine.quantity = quantity
            msg = f"Stock set to {quantity} for {medicine.name}."

        medicine.save()
        messages.success(request, msg)
        return redirect('medicine_list')

    return render(request, 'stockkeeper/update_stock.html', {'medicine': medicine})


@stockkeeper_required
def edit_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.name          = request.POST['name']
        medicine.batch_number  = request.POST['batch_number']
        medicine.supplier      = request.POST['supplier']
        medicine.minimum_stock = int(request.POST['minimum_stock'])
        medicine.expiry_date   = request.POST['expiry_date']
        medicine.save()
        messages.success(request, f"Medicine '{medicine.name}' updated!")
        return redirect('medicine_list')

    return render(request, 'stockkeeper/edit_medicine.html', {'medicine': medicine})


@stockkeeper_required
def delete_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = medicine.name
        medicine.delete()
        messages.success(request, f"Medicine '{name}' deleted!")
        return redirect('medicine_list')
    return render(request, 'stockkeeper/delete_medicine.html', {'medicine': medicine})


@stockkeeper_required
def export_inventory_pdf(request):
    medicines = Medicine.objects.all().order_by('name')
    today     = datetime.date.today()

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph("Medicine Inventory Report", styles['Title']))
    story.append(Paragraph(f"Generated: {today.strftime('%d %B %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))

    low_stock = medicines.filter(quantity__lt=10).count()
    expired   = medicines.filter(expiry_date__lt=today).count()

    story.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ['Total Medicines', str(medicines.count())],
        ['Low Stock Items', str(low_stock)],
        ['Expired Items',   str(expired)],
    ]
    t_summary = Table(summary_data, colWidths=[200, 300])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 10),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Full Inventory", styles['Heading2']))
    inv_data = [['Medicine', 'Batch No.', 'Supplier', 'Qty', 'Min', 'Expiry', 'Status']]
    for m in medicines:
        if m.expiry_date < today:
            status = 'Expired'
        elif m.quantity < m.minimum_stock:
            status = 'Low Stock'
        else:
            status = 'OK'
        inv_data.append([
            m.name,
            m.batch_number,
            m.supplier,
            str(m.quantity),
            str(m.minimum_stock),
            m.expiry_date.strftime('%d-%m-%Y'),
            status,
        ])

    t_inv = Table(inv_data, colWidths=[90, 70, 80, 35, 35, 70, 65])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 8),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 5),
    ]))
    story.append(t_inv)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'
    return response