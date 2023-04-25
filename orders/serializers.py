from rest_framework import serializers

from products.serializers import ProductSerializer

from .models import Order, ShoppingCart


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class ShoppingCartDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        # extra_kwargs = {"delivery_address": {"required": True}}
