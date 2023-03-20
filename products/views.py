from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.models import Category
from categories.serializers import CategorySerializer
from users.permissions import is_in_group
from users.views import CustomJWTAuthentication

from .models import Color, Picture, Product, Storage
from .serializers import (
    ColorSerializer,
    PictureSerializer,
    ProductSerializer,
    StorageSerializer,
)


def pic_ids_as_address_list(pic_ids):
    return [Picture.objects.get(id=pic_id).picture_address.name for pic_id in pic_ids]


def color_check_create(instance):
    try:
        color = int(instance["color"])
    except ValueError:
        color = instance["color"]
    color_is_string = isinstance(color, str)
    if color_is_string:
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


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter", label="Search")
    category = filters.ModelMultipleChoiceFilter(queryset=Category.objects.all())
    color = filters.ModelMultipleChoiceFilter(queryset=Color.objects.all())

    class Meta:
        model = Product
        fields = ["search", "category", "color"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(free_description__icontains=value)
        )


class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    pagination_class = ProductListPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "free_description"]
    ordering_fields = ["id"]
    ordering = ["id"]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = Product.objects.all()
        all_products = self.request.query_params.get("all")
        if not is_in_group(self.request.user, "storage_group") or all_products is None:
            queryset = queryset.filter(available=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for product in serializer.data:
                product["pictures"] = pic_ids_as_address_list(product["pictures"])
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request_data = request.data
        productinstance = color_check_create(request_data)
        try:
            productinstance["group_id"] = Product.objects.latest("id").id + 1
        except ObjectDoesNotExist:
            productinstance["group_id"] = 1
        modified_request = [productinstance] * int(request.data["amount"])
        serializer = ProductSerializer(data=modified_request, many=True)
        serializer.is_valid(raise_exception=True)
        products = serializer.save()
        picture_ids = []
        for file in request.FILES.getlist("pictures[]"):
            ext = file.content_type.split("/")[1]
            pic_serializer = PictureSerializer(
                data={
                    "picture_address": ContentFile(
                        file.read(), name=f"{timezone.now().timestamp()}.{ext}"
                    )
                }
            )  # use creation date as name?
            pic_serializer.is_valid(raise_exception=True)
            self.perform_create(pic_serializer)
            picture_ids.append(pic_serializer.data["id"])

        # combine pic_ids_as_address_list with enumerate loop?
        for product in products:
            for picture_id in picture_ids:
                product.pictures.add(picture_id)

        for i in range(len(serializer.data)):
            serializer.data[i]["pictures"] = pic_ids_as_address_list(
                serializer.data[i]["pictures"]
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


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


class CategoriesByIdListView(APIView):
    """View that returns self and child categories with given id in url"""

    def get_queryset(self):
        category = Category.objects.get(id=self.kwargs["category_id"])
        categories = category.get_descendants(include_self=True)
        return Category.objects.filter(id__in=categories)

    def get(self, request, *args, **kwargs):
        category_ids = [category.id for category in self.get_queryset()]
        return Response(category_ids)


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

    def create(self, request, *args, **kwargs):
        for file in request.FILES.values():
            ext = file.content_type.split("/")[1]
            serializer = self.get_serializer(
                data={
                    "picture_address": ContentFile(
                        file.read(), name=f"{timezone.now().timestamp()}.{ext}"
                    )
                }
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class PictureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class ProductStorageTransferView(APIView):
    """View for transfering list of products to different storage"""

    def put(self, request, *args, **kwargs):
        storage = Storage.objects.get(id=request.data["storage"])
        products = Product.objects.filter(id__in=request.data["products"])
        products.update(storages=storage)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
