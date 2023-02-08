from rest_framework import serializers

from .models import Order, ShoppingCart
from .models import Product

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"

class testSer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    
    all_product_info = testSer(read_only=True, many=True) #MIKSI EI TOIMIIIIIIIIS
    test2 = serializers.CharField(default="test2")

    class Meta:
        model = Order
        fields = "__all__"
