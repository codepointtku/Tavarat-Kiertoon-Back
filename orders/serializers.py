from rest_framework import serializers

from products.serializers import (
    ProductItemSchemaResponseSerializer,
    ProductItemSerializer,
)

from .models import Order, ShoppingCart


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"
        extra_kwargs = {"user": {"required": True}}


class ShoppingCartResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"
        extra_kwargs = {"user": {"required": True}}


class ShoppingCartDetailSerializer(serializers.ModelSerializer):
    product_items = ProductItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        extra_kwargs = {"user": {"required": True}}


class ShoppingCartDetailRequestSerializer(serializers.Serializer):
    product_items = serializers.IntegerField(required=False)
    amount = serializers.IntegerField()


class ShoppingCartDetailResponseSerializer(ShoppingCartResponseSerializer):
    product_items = ProductItemSchemaResponseSerializer(many=True, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ["product_items", "user"]


class OrderResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            "order_info": {"required": True},
            "delivery_date": {"required": True},
            "user": {"required": True},
            "product_items": {"required": True},
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    product_items = ProductItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderDetailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {"product_items": {"required": True}}


class OrderDetailResponseSerializer(serializers.ModelSerializer):
    product_items = ProductItemSchemaResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            "order_info": {"required": True},
            "delivery_date": {"required": True},
            "user": {"required": True},
            "product_items": {"required": True},
        }
