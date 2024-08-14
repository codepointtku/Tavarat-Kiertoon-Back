import json
from rest_framework import serializers

from products.serializers import ProductItemResponseSerializer, ProductItemSerializer
from users.custom_functions import validate_email_domain
from users.serializers import UserFullResponseSchemaSerializer, UserFullSerializer

from .models import Order, OrderEmailRecipient, ShoppingCart
import datetime


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
    product = serializers.IntegerField(required=False)
    amount = serializers.IntegerField()


class ShoppingCartDetailResponseSerializer(ShoppingCartResponseSerializer):
    product_items = ProductItemResponseSerializer(many=True, read_only=True)


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
            "status": {"required": True},
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    product_items = ProductItemSerializer(many=True, read_only=True)
    user = UserFullSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderDetailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {"product_items": {"required": True}}


class OrderDetailResponseSerializer(serializers.ModelSerializer):
    product_items = ProductItemResponseSerializer(many=True, read_only=True)
    user = UserFullResponseSchemaSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            "order_info": {"required": True},
            "delivery_date": {"required": True},
            "user": {"required": True},
            "product_items": {"required": True},
            "status": {"required": True},
        }


class OrderEmailRecipientSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if validate_email_domain(data["email"]):
            return data
        raise serializers.ValidationError("Email must be valid.")

    class Meta:
        model = OrderEmailRecipient
        fields = "__all__"


class OrderStatSerializer(serializers.ModelSerializer):
    order_year = serializers.DateTimeField(format="%Y", source="creation_date")
    order_month = serializers.DateTimeField(format="%m", source="creation_date")
    order_count = serializers.SerializerMethodField("get_order_dict")
    order_year_total = serializers.SerializerMethodField("get_yearly_total")

    class Meta:
        model = Order
        fields = ["order_year", "order_month", "order_count", "order_year_total"]

    def get_yearly_total(self, obj):
        return (
            Order.objects.filter(creation_date__year=obj.creation_date.year).count(),
        )

    def get_order_dict(self, obj):
        return {
            "order_month": obj.creation_date.month,
            "order_count": Order.objects.filter(
                creation_date__year=obj.creation_date.year
            )
            .filter(creation_date__month=obj.creation_date.month)
            .count(),
        }
