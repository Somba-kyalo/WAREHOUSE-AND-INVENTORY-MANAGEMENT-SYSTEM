from uuid import uuid4
from django.db import transaction
from django.db.models import F
from .models import AuditLog, Notification, PurchaseOrder, StockItem, StockTransaction, StockTransfer

class InventoryError(Exception): pass

@transaction.atomic
def change_stock(*, product, warehouse, quantity, transaction_type, user=None, notes=''):
    if quantity == 0: raise InventoryError('Quantity must not be zero.')
    stock, _ = StockItem.objects.select_for_update().get_or_create(product=product, warehouse=warehouse)
    previous = stock.quantity; new_quantity = previous + quantity
    if new_quantity < 0 or stock.reserved_quantity > new_quantity: raise InventoryError('Insufficient available stock.')
    stock.quantity = new_quantity; stock.save(update_fields=['quantity', 'updated_at'])
    StockTransaction.objects.create(transaction_reference=f'TXN-{uuid4().hex[:10].upper()}', product=product, warehouse=warehouse, transaction_type=transaction_type, quantity=abs(quantity), previous_quantity=previous, new_quantity=new_quantity, performed_by=user, notes=notes)
    return stock

def stock_in(product, warehouse, quantity, user=None, notes=''): return change_stock(product=product, warehouse=warehouse, quantity=quantity, transaction_type='STOCK_IN', user=user, notes=notes)
def stock_out(product, warehouse, quantity, user=None, notes=''): return change_stock(product=product, warehouse=warehouse, quantity=-quantity, transaction_type='STOCK_OUT', user=user, notes=notes)

@transaction.atomic
def transfer_stock(*, product, source, destination, quantity, user=None, notes=''):
    if source.pk == destination.pk: raise InventoryError('Source and destination warehouses must be different.')
    stock_out(product, source, quantity, user=user, notes=notes)
    stock_in(product, destination, quantity, user=user, notes=notes)
    return StockItem.objects.get(product=product, warehouse=destination)

@transaction.atomic
def receive_purchase_order(order: PurchaseOrder, receipts: dict, user=None):
    if order.status in {'CANCELLED', 'RECEIVED'}: raise InventoryError('This purchase order cannot receive more stock.')
    for item in order.items.select_related('product'):
        received = int(receipts.get(str(item.product_id), 0))
        if received < 0 or item.received_quantity + received > item.quantity: raise InventoryError(f'Receipt exceeds ordered quantity for {item.product.name}.')
        if received:
            stock_in(item.product, order.warehouse, received, user=user, notes=f'Received against {order.order_number}')
            item.received_quantity += received; item.save(update_fields=['received_quantity'])
    order.status = 'RECEIVED' if all(i.received_quantity == i.quantity for i in order.items.all()) else 'PARTIAL'
    order.save(update_fields=['status', 'updated_at'])
    AuditLog.objects.create(user=user, action='receive_purchase_order', model_name='PurchaseOrder', record_identifier=order.order_number, details={'receipts': receipts})
    return order

def create_low_stock_alerts(user=None):
    items = StockItem.objects.select_related('product', 'warehouse').filter(quantity__lte=F('product__reorder_threshold'))
    created = 0
    for item in items:
        title = f'{item.product.name} needs replenishment'
        if not Notification.objects.filter(recipient=user, title=title, is_read=False).exists():
            Notification.objects.create(recipient=user, title=title, message=f'{item.warehouse.name} has {item.available_quantity} available.', notification_type='LOW_STOCK'); created += 1
    return created

