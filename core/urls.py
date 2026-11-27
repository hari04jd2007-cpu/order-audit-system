from django.urls import path
from . import views

urlpatterns = [
    path(
        "invoice/<int:invoice_id>/pdf/",
        views.invoice_pdf,
        name="invoice_pdf"
    ),
    path(
        "reports/sales-register/",
        views.sales_register_csv,
        name="sales_register_csv"
    ),
    path(
        "reports/stock-summary/",
        views.stock_summary_csv,
        name="stock_summary_csv"
    ),
]