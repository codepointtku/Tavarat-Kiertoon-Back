from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from categories.models import Category
from .models import Product, Color, Picture, Storage
from .serializers import ProductSerializer, ColorSerializer, PictureSerializer, StorageSerializer

# Create your views here.
class ProductListPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"


class CategoryProductListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductListPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["date", "name", "color"]
    ordering = ["date", "name", "color"]


class CategoryProductListView(generics.ListAPIView):
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


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class ColorListView(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class StorageListView(generics.ListCreateAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


class PictureListView(generics.ListCreateAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class PictureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer
