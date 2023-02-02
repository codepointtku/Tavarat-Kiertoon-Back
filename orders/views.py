from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response

from products.models import Product

from .models import Order, ShoppingCart
from .serializers import OrderSerializer, ShoppingCartSerializer

# Create your views here.


class ShoppingCartListView(ListCreateAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class ShoppingCartDetailView(RetrieveDestroyAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class OrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def product_availibility_check(self, user_id):
        shopping_cart = ShoppingCart.objects.get(user_id=user_id)
        product_list = shopping_cart.products.all()
        available_products = []
        for product in product_list:
            if product.available == True:
                available_products.append(product.id)
            else:
                for same_product in Product.objects.filter(group_id=product.group_id):
                    if (
                        same_product.available == True
                        and same_product.id not in available_products
                    ):
                        available_products.append(same_product.id)
                        break
        return available_products

    def post(self, request, *args, **kwargs):
        user_id = request.data["user"]
        available_products_ids = self.product_availibility_check(user_id)
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.get(id=serializer.data["id"])
            for product_id in available_products_ids:
                order.products.add(product_id)
            updated_serializer = OrderSerializer(order).data
            return Response(updated_serializer)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Order not created


class OrderDetailView(RetrieveDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
