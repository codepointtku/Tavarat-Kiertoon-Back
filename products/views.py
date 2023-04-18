from functools import reduce
from operator import and_, or_

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Count, Q
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
    page_size = 30
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

    def search_filter(self, queryset, value, *args, **kwargs):
        word_list = args[0].split(" ")

        def filter_function(operator):
            """Function that takes operator like 'and_' or 'or_' and returns reduced queryset
            of products that have word of wordlist contained in name or free_description
            """
            qs = queryset.filter(
                reduce(
                    operator,
                    (
                        Q(name__icontains=word) | Q(free_description__icontains=word)
                        for word in word_list
                    ),
                )
            )
            qs._hints["filter"] = operator.__name__.strip("_")
            return qs

        """Creates queryset with and_ and if its empty it creates new queryset with or_"""
        and_queryset = filter_function(and_)
        if and_queryset.count():
            return and_queryset
        or_queryset = filter_function(or_)
        return or_queryset


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(available=True)
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
    ordering_fields = ["modified_date", "id"]
    ordering = ["-modified_date", "-id"]
    filterset_class = ProductFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        unique_groupids = (
            queryset.values("id")
            .order_by("group_id", "-modified_date")
            .distinct("group_id")
        )
        grouped_queryset = queryset.filter(id__in=unique_groupids)
        amounts = (
            queryset.values("group_id")
            .order_by("group_id")
            .annotate(amount=Count("group_id"))
        )
        page = self.paginate_queryset(grouped_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for product in serializer.data:
                product["pictures"] = pic_ids_as_address_list(product["pictures"])
                product["amount"] = amounts.filter(group_id=product["group_id"])[0][
                    "amount"
                ]
            response = self.get_paginated_response(serializer.data)
            if queryset._hints:
                response.data["filter"] = queryset._hints["filter"]
            return Response(response.data)
        serializer = self.get_serializer(grouped_queryset, many=True)
        return Response(serializer.data)


class StorageProductListView(generics.ListCreateAPIView):
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
    ordering_fields = ["modified_date", "id"]
    ordering = ["-modified_date", "-id"]
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
            )
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
        if "modify_date" in request.data:
            serializer.save(modified_date=timezone.now())
        else:
            serializer.save()
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
        amount = self.queryset.filter(group_id=data["group_id"], available=True).count()
        data["amount"] = amount
        data["pictures"] = pic_ids_as_address_list(data["pictures"])
        return Response(data)


class CategoryTreeView(APIView):
    """Returns all category ids as keys and all level 2 child categories of that category as list"""

    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        category_tree = {
            c.id: [c.id for c in c.get_descendants(include_self=True).filter(level=2)]
            for c in self.queryset.all()
        }
        return Response(category_tree)


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
