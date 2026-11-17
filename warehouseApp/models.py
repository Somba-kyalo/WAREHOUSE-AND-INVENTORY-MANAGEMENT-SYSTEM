from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=160); warehouse_code = models.CharField(max_length=30, unique=True); location = models.CharField(max_length=180); description = models.TextField(blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=[('ACTIVE','Active'),('INACTIVE','Inactive')], default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f'{self.name} ({self.warehouse_code})'

class Product(models.Model):
    sku = models.CharField(max_length=60, unique=True); barcode = models.CharField(max_length=80, unique=True, null=True, blank=True); name = models.CharField(max_length=180); description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL); brand = models.CharField(max_length=120, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]); cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reorder_threshold = models.PositiveIntegerField(default=0); unit_of_measure = models.CharField(max_length=30, default='units'); status = models.CharField(max_length=10, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)

class StockItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE); warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE); quantity = models.PositiveIntegerField(default=0); reserved_quantity = models.PositiveIntegerField(default=0); updated_at = models.DateTimeField(auto_now=True)
    class Meta: constraints = [models.UniqueConstraint(fields=['product', 'warehouse'], name='unique_product_warehouse')]
    @property
    def available_quantity(self): return self.quantity - self.reserved_quantity

class StockTransaction(models.Model):
    transaction_reference = models.CharField(max_length=40, unique=True); product = models.ForeignKey(Product, on_delete=models.PROTECT); warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT); transaction_type = models.CharField(max_length=20); quantity = models.IntegerField(); previous_quantity = models.PositiveIntegerField(); new_quantity = models.PositiveIntegerField(); performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL); notes = models.TextField(blank=True); created_at = models.DateTimeField(auto_now_add=True)

class Supplier(models.Model):
    name = models.CharField(max_length=180); contact_person = models.CharField(max_length=120, blank=True); email = models.EmailField(blank=True); phone = models.CharField(max_length=40, blank=True); address = models.TextField(blank=True); tax_number = models.CharField(max_length=80, blank=True); status = models.CharField(max_length=12, default='ACTIVE'); created_at = models.DateTimeField(auto_now_add=True)

class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=40, unique=True); supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT); warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT); created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL); order_date = models.DateField(auto_now_add=True); expected_delivery_date = models.DateField(null=True, blank=True); status = models.CharField(max_length=20, default='DRAFT'); total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE); product = models.ForeignKey(Product, on_delete=models.PROTECT); quantity = models.PositiveIntegerField(); unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]); received_quantity = models.PositiveIntegerField(default=0)
    class Meta: constraints = [models.UniqueConstraint(fields=['purchase_order', 'product'], name='unique_purchase_product')]

class StockTransfer(models.Model):
    transfer_reference = models.CharField(max_length=40, unique=True); source_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.PROTECT); destination_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.PROTECT); initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='initiated_transfers', on_delete=models.SET_NULL); approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='approved_transfers', on_delete=models.SET_NULL); status = models.CharField(max_length=20, default='PENDING'); notes = models.TextField(blank=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)

class StockTransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE); product = models.ForeignKey(Product, on_delete=models.PROTECT); quantity = models.PositiveIntegerField()

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE); title = models.CharField(max_length=180); message = models.TextField(); notification_type = models.CharField(max_length=30); is_read = models.BooleanField(default=False); created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL); action = models.CharField(max_length=80); model_name = models.CharField(max_length=120); record_identifier = models.CharField(max_length=120); details = models.JSONField(default=dict, blank=True); created_at = models.DateTimeField(auto_now_add=True)

