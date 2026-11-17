from rest_framework import serializers
from .models import AuditLog, Category, Notification, Product, PurchaseOrder, PurchaseOrderItem, StockItem, StockTransaction, StockTransfer, Supplier, Warehouse
class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = '__all__'
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta: model = Warehouse; fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta: model = Product; fields = '__all__'
class StockItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True); sku = serializers.CharField(source='product.sku', read_only=True); warehouse_name = serializers.CharField(source='warehouse.name', read_only=True); available_quantity = serializers.IntegerField(read_only=True); stock_status = serializers.SerializerMethodField()
    def get_stock_status(self, obj):
        return 'OUT' if obj.available_quantity == 0 else ('LOW' if obj.available_quantity <= obj.product.reorder_threshold else 'OK')
    class Meta: model = StockItem; fields = ['id','product','product_name','sku','warehouse','warehouse_name','quantity','reserved_quantity','available_quantity','stock_status','updated_at']
class StockTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True); warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    class Meta: model = StockTransaction; fields = '__all__'
class SupplierSerializer(serializers.ModelSerializer):
    class Meta: model = Supplier; fields = '__all__'
class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta: model = PurchaseOrderItem; fields = '__all__'
class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    class Meta: model = PurchaseOrder; fields = '__all__'
class StockTransferSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta: model = StockTransfer; fields = '__all__'
class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model = Notification; fields = '__all__'
class AuditLogSerializer(serializers.ModelSerializer):
    class Meta: model = AuditLog; fields = '__all__'

