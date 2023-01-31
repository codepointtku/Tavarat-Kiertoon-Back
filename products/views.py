from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Product
from .serializers import ProductSerializer

# Create your views here.


class ProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        category = self.kwargs['category']
        return Product.objects.filter(category_name=category)


class ProductCategory(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, pk, format=None):
        products = self.get_object(pk)
        serializer = ProductSerializer(products)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        products = self.get_object(pk)
        serializer = ProductSerializer(products, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        products = self.get_object(pk)
        products.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
