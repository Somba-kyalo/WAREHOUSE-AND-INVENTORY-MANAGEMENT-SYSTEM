from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, CategoryViewSet, NotificationViewSet, ProductViewSet, PurchaseOrderViewSet, StockItemViewSet, StockTransactionViewSet, StockTransferViewSet, SupplierViewSet, WarehouseViewSet, dashboard
router = DefaultRouter(); router.register('categories', CategoryViewSet); router.register('products', ProductViewSet); router.register('warehouses', WarehouseViewSet); router.register('inventory', StockItemViewSet); router.register('transactions', StockTransactionViewSet); router.register('suppliers', SupplierViewSet); router.register('purchase-orders', PurchaseOrderViewSet); router.register('transfers', StockTransferViewSet); router.register('notifications', NotificationViewSet); router.register('audit', AuditLogViewSet)
urlpatterns = [path('', include(router.urls)), path('dashboard/', dashboard)]

