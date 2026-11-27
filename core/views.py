
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from .models import Invoice
import csv
from django.contrib.admin.views.decorators import staff_member_required
from .models import SalesOrder, Product, RawMaterial


@login_required
def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.sales_order
    customer = order.customer

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("GST TAX INVOICE", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"<b>Invoice Number:</b> {invoice.invoice_number}",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        f"<b>Customer:</b> {customer.name}",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        f"<b>Customer State:</b> {customer.state}",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        f"<b>GSTIN:</b> {customer.gstin or 'Not provided'}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    data = [
        ["Description", "Quantity", "Rate", "Amount"],
        [
            order.product.name,
            str(order.quantity),
            f"Rs. {order.product.selling_price}",
            f"Rs. {invoice.taxable_amount}"
        ],
        ["", "", "CGST", f"Rs. {invoice.cgst}"],
        ["", "", "SGST", f"Rs. {invoice.sgst}"],
        ["", "", "IGST", f"Rs. {invoice.igst}"],
        ["", "", "Total", f"Rs. {invoice.total_amount}"],
        ["", "", "Paid", f"Rs. {invoice.amount_paid}"],
        ["", "", "Outstanding", f"Rs. {invoice.outstanding}"],
    ]

    table = Table(data, colWidths=[180, 80, 100, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for your business!", styles["Normal"]))

    pdf.build(elements)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{invoice.invoice_number}.pdf"'
    )

    return response

@staff_member_required
def sales_register_csv(request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sales_register.csv"'

        writer = csv.writer(response)
        writer.writerow([
        "Order ID",
        "Customer",
        "State",
        "Product",
        "Quantity",
        "Status"
        ])

        orders = SalesOrder.objects.select_related("customer", "product")

        for order in orders:
            writer.writerow([
            order.id,
            order.customer.name,
            order.customer.state,
            order.product.name,
            order.quantity,
            order.status
           ])

        return response


@staff_member_required
def stock_summary_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="stock_summary.csv"'

    writer = csv.writer(response)

    writer.writerow(["Finished Product", "Available Stock"])

    for product in Product.objects.all():
        writer.writerow([product.name, product.stock])

    writer.writerow([])
    writer.writerow(["Raw Material", "Unit", "Available Quantity"])

    for material in RawMaterial.objects.all():
        writer.writerow([
            material.name,
            material.unit,
            material.stock_quantity
        ])

    return response