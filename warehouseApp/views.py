from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import AuditLog, Category, Notification, Product, PurchaseOrder, StockItem, StockTransaction, StockTransfer, Supplier, Warehouse
from .serializers import AuditLogSerializer, CategorySerializer, NotificationSerializer, ProductSerializer, PurchaseOrderSerializer, StockItemSerializer, StockTransactionSerializer, StockTransferSerializer, SupplierSerializer, WarehouseSerializer
from .services import stock_in, stock_out, transfer_stock, InventoryError
class CategoryViewSet(viewsets.ModelViewSet): queryset = Category.objects.all(); serializer_class = CategorySerializer
class WarehouseViewSet(viewsets.ModelViewSet): queryset = Warehouse.objects.all(); serializer_class = WarehouseSerializer
class ProductViewSet(viewsets.ModelViewSet): queryset = Product.objects.select_related('category').all(); serializer_class = ProductSerializer
class StockItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockItem.objects.select_related('product','warehouse').all(); serializer_class = StockItemSerializer
    @action(detail=False, methods=['post'], url_path='move')
    def move(self, request):
        try:
            product = Product.objects.get(pk=request.data['product']); warehouse = Warehouse.objects.get(pk=request.data['warehouse'])
            fn = stock_in if request.data['type'] == 'STOCK_IN' else stock_out
            return Response(StockItemSerializer(fn(product, warehouse, int(request.data['quantity']), notes=request.data.get('notes',''))).data)
        except (KeyError, ValueError, Product.DoesNotExist, Warehouse.DoesNotExist, InventoryError) as exc: return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet): queryset = StockTransaction.objects.select_related('product','warehouse').order_by('-created_at'); serializer_class = StockTransactionSerializer
class SupplierViewSet(viewsets.ModelViewSet): queryset = Supplier.objects.all(); serializer_class = SupplierSerializer
class PurchaseOrderViewSet(viewsets.ModelViewSet): queryset = PurchaseOrder.objects.select_related('supplier','warehouse').prefetch_related('items').all(); serializer_class = PurchaseOrderSerializer
class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.select_related('source_warehouse','destination_warehouse').prefetch_related('items').all()
    serializer_class = StockTransferSerializer
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        transfer = self.get_object()
        try:
            for item in transfer.items.select_related('product'):
                transfer_stock(product=item.product, source=transfer.source_warehouse, destination=transfer.destination_warehouse, quantity=item.quantity, user=request.user if request.user.is_authenticated else None, notes=transfer.transfer_reference)
            transfer.status = 'COMPLETED'; transfer.save(update_fields=['status', 'updated_at']); return Response(self.get_serializer(transfer).data)
        except InventoryError as exc: return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
class NotificationViewSet(viewsets.ModelViewSet): queryset = Notification.objects.order_by('-created_at'); serializer_class = NotificationSerializer
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet): queryset = AuditLog.objects.order_by('-created_at'); serializer_class = AuditLogSerializer
@api_view(['GET'])
def dashboard(request):
    items = list(StockItem.objects.select_related('product','warehouse')); total = items and sum(i.quantity for i in items) or 0
    return Response({'products': Product.objects.filter(status='ACTIVE').count(), 'warehouses': Warehouse.objects.filter(status='ACTIVE').count(), 'units': total, 'valuation': sum((i.quantity * i.product.cost_price for i in items), 0), 'low_stock': sum(1 for i in items if 0 < i.available_quantity <= i.product.reorder_threshold), 'out_of_stock': sum(1 for i in items if i.available_quantity == 0), 'recent_transactions': StockTransactionSerializer(StockTransaction.objects.select_related('product','warehouse').order_by('-created_at')[:6], many=True).data})

