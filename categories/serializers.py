from rest_framework import serializers

from products.models import Product

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    def get_product_count(self, obj):
        categories = obj.get_descendants(include_self=True)
        products = Product.objects.filter(available=True)
        return products.filter(category__in=categories).count()

    class Meta:
        model = Category
        fields = "__all__"
