
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    gstin = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class BOM(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_output = models.IntegerField(default=200)

    def __str__(self):
        return f"BOM - {self.product.name}"


class BOMItem(models.Model):
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.material.name} - {self.quantity_required}"


class ProductionRun(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    production_date = models.DateField(auto_now_add=True)

    flour_used = models.DecimalField(max_digits=10, decimal_places=2)
    oil_used = models.DecimalField(max_digits=10, decimal_places=2)
    spice_used = models.DecimalField(max_digits=10, decimal_places=2)
    pouches_used = models.IntegerField()
    cartons_used = models.IntegerField()

    good_packets = models.IntegerField()
    damaged_pouches = models.IntegerField(default=0)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Production - {self.product.name} - {self.good_packets} packets"

class Purchase(models.Model):
    material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_rate = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Dispatched", "Dispatched"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return f"{self.customer.name} - {self.quantity} packets"
class Invoice(models.Model):
    sales_order = models.OneToOneField(
        SalesOrder,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(max_length=30, unique=True)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.invoice_number

    @property
    def outstanding(self):
        return self.total_amount - self.amount_paid

class ProductionExpense(models.Model):
    production_run = models.OneToOneField(
        ProductionRun,
        on_delete=models.CASCADE
    )

    labour_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gas_power_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    @property
    def total_expense(self):
        return self.labour_cost + self.gas_power_cost

    def __str__(self):
        return f"Expenses - {self.production_run}"