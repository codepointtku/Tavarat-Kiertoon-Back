from functools import reduce
from operator import and_, or_

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.models import Category
from orders.models import ShoppingCart
from orders.serializers import ShoppingCartDetailSerializer
from users.permissions import is_in_group
from users.views import CustomJWTAuthentication

from .models import Color, Picture, Product, ProductItem, Storage
from .serializers import (
    ColorSerializer,
    PictureCreateSerializer,
    PictureSerializer,
    ProductCreateSchemaSerializer,
    ProductCreateSerializer,
    ProductItemDetailSchemaResponseSerializer,
    ProductItemUpdateSchemaResponseSerializer,
    ProductItemSchemaResponseSerializer,
    ProductItemSerializer,
    ProductItemUpdateSerializer,
    ProductSchemaResponseSerializer,
    ProductSerializer,
    ProductStorageTransferSerializer,
    ProductUpdateSerializer,
    ProductUpdateSchemaResponseSerializer,
    ShoppingCartAvailableAmountListSerializer,
    StorageSchemaResponseSerializer,
    StorageSerializer,
)


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


@extend_schema_view(
    post=extend_schema(
        request=ProductCreateSchemaSerializer(),
        responses=ProductSchemaResponseSerializer(),
    ),
    get=extend_schema(responses=ProductSchemaResponseSerializer()),
)
class ProductListView(generics.ListCreateAPIView):
    """View for listing and creating products. Create includes creation of ProductItem and Picture"""

    queryset = Product.objects.all()
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
    ordering = ["-id"]
    filterset_class = ProductFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            if queryset._hints:
                response.data["filter"] = queryset._hints["filter"]
            return Response(response.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        color_checked_data = color_check_create(request.data)
        serializer = ProductCreateSerializer(data=color_checked_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

        """ Picture creation logic in Product create, not in use for now"""
        # # modified_request = [product_item] * amount
        # # serializer = ProductSerializer(data=modified_request, many=True)
        # # serializer.is_valid(raise_exception=True)
        # # products = serializer.save()
        # # picture_ids = []
        # # for file in request.FILES.getlist("pictures[]"):
        # #     ext = file.content_type.split("/")[1]
        # #     pic_serializer = PictureCreateSerializer(
        # #         data={
        # #             "picture_address": ContentFile(
        # #                 file.read(), name=f"{timezone.now().timestamp()}.{ext}"
        # #             )
        # #         }
        # #     )
        # #     pic_serializer.is_valid(raise_exception=True)
        # #     self.perform_create(pic_serializer)
        # #     picture_ids.append(pic_serializer.data["id"])

        # # for product in products:
        # #     for picture_id in picture_ids:
        # #         product.pictures.add(picture_id)

        # # headers = self.get_success_headers(serializer.data)
        # # return Response(
        # #     serializer.data, status=status.HTTP_201_CREATED, headers=headers
        # # )


@extend_schema_view(
    get=extend_schema(
        responses=ProductSchemaResponseSerializer(),
    ),
    put=extend_schema(
        request=ProductUpdateSerializer(),
        responses=ProductUpdateSchemaResponseSerializer(),
    ),
    patch=extend_schema(exclude=True),
)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, (destroying) a single Product"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = ProductUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class ProductItemListPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"


class ProductItemListFilter(filters.FilterSet):
    product = filters.ModelMultipleChoiceFilter(queryset=Product.objects.all())
    storage = filters.ModelMultipleChoiceFilter(queryset=Storage.objects.all())
    available = filters.BooleanFilter()
    shelf_id = filters.AllValuesFilter()


@extend_schema_view(
    get=extend_schema(responses=ProductItemSchemaResponseSerializer()),
)
class ProductItemListView(generics.ListAPIView):
    """
    Lists all Product items
    """

    queryset = ProductItem.objects.all()
    serializer_class = ProductItemSerializer
    pagination_class = ProductListPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["modified_date", "id", "available", "product", "storage"]
    ordering = ["-modified_date", "-id"]
    filterset_class = ProductItemListFilter


@extend_schema_view(
    get=extend_schema(responses=ProductItemDetailSchemaResponseSerializer()),
    put=extend_schema(
        request=ProductItemUpdateSchemaResponseSerializer(),
        responses=ProductItemDetailSchemaResponseSerializer(),
    ),
    patch=extend_schema(exclude=True),
)
class ProductItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for modifying single Product item
    """

    queryset = ProductItem.objects.all()
    serializer_class = ProductItemUpdateSerializer

    def update(self, request, *args, **kwargs):
        """
        as modified date is read only and needs to be updated in only very specific situations.
        copypasted the functions from librarys. (mixins.UpdateModelMixin)
        when the "modify_date" value field is found in request body, only then the modified date is updated.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = ProductItemUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        if "modify_date" in request.data:
            serializer.save(modified_date=timezone.now())
        else:
            serializer.save()
        data = serializer.data

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class ColorListView(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


@extend_schema_view(
    get=extend_schema(
        responses=StorageSchemaResponseSerializer(),
    ),
    post=extend_schema(
        responses=StorageSchemaResponseSerializer(),
    ),
)
class StorageListView(generics.ListCreateAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


@extend_schema_view(
    get=extend_schema(
        responses=StorageSchemaResponseSerializer(),
    ),
    patch=extend_schema(exclude=True),
    put=extend_schema(
        responses=StorageSchemaResponseSerializer(),
    ),
)
class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


class PictureListView(generics.ListCreateAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureCreateSerializer

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


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class PictureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


# @extend_schema_view(
#     put=extend_schema(responses=ProductStorageListSerializer(many=True))
# )
class ProductStorageTransferView(APIView):
    """View for transfering list of products to different storage"""

    serializer_class = ProductStorageTransferSerializer

    def put(self, request, *args, **kwargs):
        storage = Storage.objects.get(id=request.data["storage"])
        product_items = ProductItem.objects.filter(id__in=request.data["product_items"])
        product_items.update(storage=storage)
        serializer = ProductItemSerializer(product_items, many=True)
        return Response(serializer.data)


class ShoppingCartAvailableAmountList(APIView):
    """View for getting Products in users shopping cart and their available amounts for ProductItems not already in shopping cart"""

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    serializer_class = ShoppingCartAvailableAmountListSerializer(many=True)

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response("You must be logged in to see your shoppingcart")
        try:
            instance = ShoppingCart.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response("Shopping cart for this user does not exist")
        cartserializer = ShoppingCartDetailSerializer(instance)
        product_ids = []
        duplicate_checker = []
        for Product_item in cartserializer.data["products"]:
            if Product_item["product"]["id"] not in duplicate_checker:
                product_id = Product_item["product"]["id"]
                amount = ProductItem.objects.filter(
                    product=product_id, available=True
                ).count()
                pair = {"id": product_id, "amount": amount}
                product_ids.append(pair)
                duplicate_checker.append(product_id)
        returnserializer = ShoppingCartAvailableAmountListSerializer(
            product_ids, many=True
        )
        return Response(returnserializer.data)
