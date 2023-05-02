from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from products.serializers import ProductSerializer

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
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShoppingCartDetailRequestSerializer(serializers.Serializer):
    products = serializers.IntegerField()
    amount = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ["products"]
        extra_kwargs = {"user": {"required": True}}


class OrderResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            "order_info": {"required": True},
            "delivery_date": {"required": True},
            "user": {"required": True},
            "products": {"required": True},
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderDetailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {"products": {"required": True}}


class OrderDetailResponseSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            "order_info": {"required": True},
            "delivery_date": {"required": True},
            "user": {"required": True},
            "products": {"required": True},
        }
