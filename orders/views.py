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

    def post(self, request):
        serializer = ShoppingCartSerializer(data=request.data)
        if serializer.is_valid():
            if len(ShoppingCart.objects.filter(user=request.data["user"])) != 0:
                ShoppingCart.objects.filter(user=request.data["user"]).delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartDetailView(RetrieveDestroyAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class OrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def product_availibility_check(self, user_id):
        shopping_cart = ShoppingCart.objects.get(user_id=user_id)
        product_list = shopping_cart.products.all()
        product_ids = [product.id for product in product_list]

        def available_product(product: object):
            for same_product in Product.objects.filter(group_id=product.group_id):
                if same_product.available and same_product.id not in product_ids:
                    product_ids.append(same_product.id)
                    return same_product.id

        return [
            product.id if product.available else available_product(product)
            for product in product_list
        ]

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
            return Response(updated_serializer, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(RetrieveDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(id=request.data["productId"])
        for product in order.products.all():
            if product.id == request.data["product"]:
                order.products.remove(product.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
