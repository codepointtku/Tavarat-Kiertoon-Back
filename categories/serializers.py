from rest_framework import serializers

from products.models import Product, ProductItem
from products.serializers import ProductSerializer

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    def get_product_count(self, obj) -> int:
        categories = obj.get_descendants(include_self=True)
        available_amount = Product.objects.filter(category__in=categories, productitem__in=ProductItem.objects.filter(available=True)).distinct().count()
        return available_amount
        

    class Meta:
        model = Category
        fields = "__all__"


class CategoryResponseSerializer(CategorySerializer):
    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {"parent": {"required": True}}


class CategoryTreeSerializer(serializers.Serializer):
    category_id = serializers.ListField(
        child=serializers.ModelField(model_field=Category._meta.get_field("id"))
    )
