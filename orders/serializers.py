from rest_framework import serializers

from .models import Order, Product, ShoppingCart


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"

class testSer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        #fields = "id", "price"


class OrderSerializer(serializers.ModelSerializer):
    
    #products = testSer(read_only=True, many=True) #MIKSI EI TOIMIIIIIIIIS
    #test2 = serializers.CharField(default="test2")
    #products = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Order
        fields = "__all__"
        #depth = 1
