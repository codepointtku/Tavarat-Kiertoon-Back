from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from categories.models import Category
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
    filter_backends = [OrderingFilter]
    ordering_fields = ["date", "name", "color"]
    ordering = ["date", "name", "color"]


class CategoryProductList(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CategoryProductListPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["date", "name", "color"]
    ordering = ["date", "name", "color"]

    def get_queryset(self):
        category = self.kwargs["category_id"]
        categoryset = [category]
        categories = Category.objects.filter(parent=category).values("id")
        for i in categories:
            categoryset.append(i["id"])
        return Product.objects.filter(category__in=categoryset)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
