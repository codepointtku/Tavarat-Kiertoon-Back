from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from categories.models import Category

from .models import Color, Picture, Product, Storage
from .serializers import (ColorSerializer, PictureSerializer,
                          ProductSerializer, StorageSerializer)


def pic_ids_as_address_list(pic_ids):
    return [Picture.objects.get(id=pic_id).picture_address.name for pic_id in pic_ids]


def is_color_string(colortest):
    res = isinstance(colortest, str)
    return res


def color_check_create(instance):
    color = instance["color"]
    colorstring = is_color_string(color)
    if colorstring:
        checkid = Color.objects.filter(name=color).values("id")

        if not checkid:
            newcolor = {"name": color}
            colorserializer = ColorSerializer(data=newcolor)
            if colorserializer.is_valid():
                colorserializer.save()
                checkid = Color.objects.filter(name=color).values("id")
                instance["color"] = checkid[0]["id"]
        else:
            instance["color"] = checkid[0]["id"]
    return instance


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

    def create(self, request, *args, **kwargs):
        colorinstance = request.data
        productinstance = color_check_create(colorinstance[0])
        modified_request = [productinstance for i in range(request.data[1])]
        serializer = ProductSerializer(data=modified_request, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        for i in range(len(serializer.data)):
            serializer.data[i]["pictures"] = pic_ids_as_address_list(
                serializer.data[i]["pictures"]
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data["pictures"] = pic_ids_as_address_list(data["pictures"])

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["pictures"] = pic_ids_as_address_list(data["pictures"])
        return Response(data)


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
