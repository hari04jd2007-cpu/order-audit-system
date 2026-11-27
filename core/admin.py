from django.contrib import admin
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Product, Customer, RawMaterial, BOM, BOMItem, ProductionRun , Purchase,SalesOrder , Invoice ,ProductionExpense
from django.urls import reverse
from django.utils.html import format_html


admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(RawMaterial)
admin.site.register(BOM)
admin.site.register(BOMItem)


@admin.register(ProductionRun)
class ProductionRunAdmin(admin.ModelAdmin):
    list_display = (
    "product",
    "good_packets",
    "production_date",
    "yield_variance",
    "oil_variance",
    "cost_per_packet",
)
    def yield_variance(self, obj):
        bom = obj.product.bom_set.first()

        if not bom or not bom.batch_output:
            return "N/A"

        variance = (
            (obj.good_packets - bom.batch_output)
            / bom.batch_output
        ) * 100

        return f"{variance:+.1f}%"

    yield_variance.short_description = "Yield Variance"

    def oil_variance(self, obj):
        bom = obj.product.bom_set.first()

        if not bom:
            return "N/A"

        oil_item = BOMItem.objects.filter(
            bom=bom,
            material__name__iexact="oil"
        ).first()

        if not oil_item or not oil_item.quantity_required:
            return "N/A"

        variance = (
            (obj.oil_used - oil_item.quantity_required)
            / oil_item.quantity_required
        ) * 100

        return f"{variance:+.1f}%"

    oil_variance.short_description = "Oil Variance"
    def cost_per_packet(self, obj):
        expense = getattr(obj, "productionexpense", None)

        if not obj.good_packets:
            return "N/A"

        bom = obj.product.bom_set.first()

        if not bom:
            return "N/A"

        material_cost = 0

        for item in BOMItem.objects.filter(bom=bom):
            material = item.material

            if material.name.lower() == "flour":
                quantity = obj.flour_used
            elif material.name.lower() == "oil":
                quantity = obj.oil_used
            elif material.name.lower() == "spice":
                quantity = obj.spice_used
            elif material.name.lower() == "pouches":
                quantity = obj.pouches_used + obj.damaged_pouches
            elif material.name.lower() == "cartons":
                quantity = obj.cartons_used
            else:
                continue

            material_cost += quantity * material.unit_rate

        total_cost = material_cost

        if expense:
            total_cost += expense.labour_cost + expense.gas_power_cost

        return f"₹{total_cost / obj.good_packets:.2f}"

    cost_per_packet.short_description = "Cost / Packet"
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if change:
            raise ValidationError("Existing production records cannot be edited.")

        materials = {
          "flour": obj.flour_used,
           "oil": obj.oil_used,
           "Spice": obj.spice_used,
           "pouches": obj.pouches_used + obj.damaged_pouches,
           "cartons": obj.cartons_used,
        }

        for name, quantity in materials.items():
            material = RawMaterial.objects.select_for_update().get(name__iexact=name)

            if material.stock_quantity < quantity:
                raise ValidationError(
                    f"Insufficient {name} stock. Available: {material.stock_quantity}"
                )

            material.stock_quantity -= quantity
            material.save()

        obj.product.stock += obj.good_packets
        obj.product.save()

        super().save_model(request, obj, form, change)
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("material", "quantity", "unit_rate", "purchase_date")

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if change:
            raise ValidationError("Existing purchase records cannot be edited.")

        material = RawMaterial.objects.select_for_update().get(pk=obj.material_id)
        material.stock_quantity += obj.quantity
        material.unit_rate = obj.unit_rate
        material.save()

        super().save_model(request, obj, form, change)

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "quantity", "order_date", "status")
    list_filter = ("status", "order_date")
    actions = ["approve_orders", "dispatch_orders" , "generate_invoices"]

    @admin.action(description="Approve selected orders")
    def approve_orders(self, request, queryset):
        queryset.filter(status="Pending").update(status="Approved")

    @admin.action(description="Dispatch approved orders")
    def dispatch_orders(self, request, queryset):
        from django.db import transaction

        for order in queryset.filter(status="Approved"):
            with transaction.atomic():
                product = Product.objects.select_for_update().get(
                    pk=order.product_id
                )

                if product.stock < order.quantity:
                    self.message_user(
                        request,
                        f"Insufficient stock for {order.customer.name}.",
                        level="ERROR"
                    )
                    continue

                product.stock -= order.quantity
                product.save()

                order.status = "Dispatched"
                order.save()

        self.message_user(request, "Dispatch processing completed.")
    @admin.action(description="Generate GST invoices")
    def generate_invoices(self, request, queryset):
        for order in queryset.filter(status="Dispatched"):
            if Invoice.objects.filter(sales_order=order).exists():
                continue

            taxable = order.quantity * order.product.selling_price
            tax_rate = Decimal("0.025")

            if order.customer.state.strip().lower() == "tamil nadu":
                cgst = taxable * tax_rate
                sgst = taxable * tax_rate
                igst = Decimal("0.00")
            else:
                cgst = Decimal("0.00")
                sgst = Decimal("0.00")
                igst = taxable * Decimal("0.05")

            total = taxable + cgst + sgst + igst

            Invoice.objects.create(
            sales_order=order,
            invoice_number=f"INV-{order.id:04d}",
            taxable_amount=taxable,
            cgst=cgst,
            sgst=sgst,
            igst=igst,
            total_amount=total
            )

        self.message_user(request, "Invoice generation completed.")

   
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "sales_order",
        "taxable_amount",
        "total_amount",
        "amount_paid",
        "download_pdf",
    )

    @admin.display(description="PDF")
    def download_pdf(self, obj):
        url = reverse("invoice_pdf", args=[obj.id])
        return format_html(
            '<a href="{}">Download PDF</a>',
            url
        )
    @admin.register(ProductionExpense)
    class ProductionExpenseAdmin(admin.ModelAdmin):
        list_display = (
        "production_run",
        "labour_cost",
        "gas_power_cost",
        "total_expense",
     )