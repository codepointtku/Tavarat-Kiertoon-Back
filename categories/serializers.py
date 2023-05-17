from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    def get_product_count(self, obj) -> int:
        categories = obj.get_descendants(include_self=True)
        products = Product.objects.filter(category__in=categories)
        available_checker = ProductSerializer(instance=products, many=True)
        available_amount = 0
        for i in available_checker.data:
            if i["amount"] >= 1:
                available_amount += 1

        return (
            available_amount
        )

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
