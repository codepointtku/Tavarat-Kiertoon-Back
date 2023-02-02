from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import ProductSerializer

# Create your views here.
class ProductListPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"


class CategoryProductListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductListPagination


class CategoryProductList(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CategoryProductListPagination

    def get_queryset(self):
        category = self.kwargs["category_id"]
        return Product.objects.filter(category=category)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
