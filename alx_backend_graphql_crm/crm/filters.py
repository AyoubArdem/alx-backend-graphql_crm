import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    phone_pattern = django_filters.CharFilter(method="phone_pattern_filter")

    def phone_pattern_filter(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = {
            "name": ["icontains"],
            "created_at": ["gte", "lte"],
        }


class ProductFilter(django_filters.FilterSet):
    low_stock = django_filters.NumberFilter(method="filter_low_stock")

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=value)
        return queryset

    class Meta:
        model = Product
        fields = {
            "name": ["icontains"],
            "price": ["gte", "lte"],
            "stock": ["gte", "lte"],
        }


class OrderFilter(django_filters.FilterSet):
    product_id = django_filters.NumberFilter(method="filter_product_id")

    def filter_product_id(self, queryset, name, value):
        return queryset.filter(product__id=value)

    class Meta:
        model = Order
        fields = {
            "total_amount": ["gte", "lte"],
            "order_date": ["gte", "lte"],
            "product__name": ["icontains"],
            "customer__name": ["icontains"],
        }

