from django.contrib import admin
from .models import AuditLog, Category, Notification, Product, PurchaseOrder, PurchaseOrderItem, StockItem, StockTransaction, StockTransfer, StockTransferItem, Supplier, Warehouse
admin.site.register([AuditLog, Category, Notification, Product, PurchaseOrder, PurchaseOrderItem, StockItem, StockTransaction, StockTransfer, StockTransferItem, Supplier, Warehouse])

