from decimal import Decimal
from django.core.management.base import BaseCommand
from warehouseApp.models import Category, Product, StockItem, Warehouse

class Command(BaseCommand):
    help = 'Create a small, repeatable local warehouse dataset.'
    def handle(self, *args, **options):
        category, _ = Category.objects.get_or_create(name='Packaging', defaults={'description':'Consumable packing materials'})
        central, _ = Warehouse.objects.get_or_create(warehouse_code='NBO-01', defaults={'name':'Central depot','location':'Industrial Area'})
        west, _ = Warehouse.objects.get_or_create(warehouse_code='NBO-02', defaults={'name':'Westlands','location':'Westlands'})
        products = [
            ('LAB-0046','Thermal labels 4×6',40,18), ('SCN-2210','Handheld scanner · Zebra TC',6,0), ('PKG-0500','Pallet wrap 500m',30,22),
        ]
        for sku, name, threshold, quantity in products:
            product, _ = Product.objects.get_or_create(sku=sku, defaults={'name':name,'category':category,'unit_price':Decimal('18.00'),'cost_price':Decimal('11.50'),'reorder_threshold':threshold})
            StockItem.objects.update_or_create(product=product, warehouse=central, defaults={'quantity':quantity, 'reserved_quantity':0})
        StockItem.objects.get_or_create(product=Product.objects.get(sku='LAB-0046'), warehouse=west, defaults={'quantity':60, 'reserved_quantity':4})
        self.stdout.write(self.style.SUCCESS('Demo warehouse data is ready.'))
