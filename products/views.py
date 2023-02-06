from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from categories.models import Category

from .models import Color, Picture, Product, Storage
from .serializers import (
    ColorSerializer,
    PictureSerializer,
    ProductSerializer,
    StorageSerializer,
)


def pic_ids_as_address_list(pic_ids):
    return [Picture.objects.get(id=pic_id).picture_address.name for pic_id in pic_ids]


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

    # def get(self, request, *args, **kwargs):
    #     products = Product.objects.all()
    #     serializer = ProductSerializer(products, many=True)
    #     # data = pictures_as_address_list(serializer)
    #     print(serializer.data)
    #     return Response(serializer.data)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for i in range(len(serializer.data)):
                serializer.data[i]["pictures"] = pic_ids_as_address_list(
                    serializer.data[i]["pictures"]
                )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data["pictures"] = pic_ids_as_address_list(data["pictures"])
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
