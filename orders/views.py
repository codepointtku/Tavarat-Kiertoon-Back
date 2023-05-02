from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product
from users.views import CustomJWTAuthentication

from .models import Order, ShoppingCart
from .serializers import (
    OrderDetailRequestSerializer,
    OrderDetailSerializer,
    OrderRequestSerializer,
    OrderSerializer,
    ShoppingCartDetailRequestSerializer,
    ShoppingCartDetailSerializer,
    ShoppingCartSerializer,
)


# Create your views here.
def product_availibility_check(user_id):
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


class ShoppingCartDetailView(RetrieveUpdateAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartDetailSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response("You must be logged in to see your shoppingcart")
        try:
            instance = ShoppingCart.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response("Shopping cart for this user does not exist")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(request=ShoppingCartDetailRequestSerializer)
    def put(self, request, *args, **kwargs):
        try:
            instance = ShoppingCart.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response("Shopping cart for this user does not exist")
        # if amount is 0, clear users ShoppingCart
        if request.data["amount"] == 0:
            instance.products.clear()
            updatedinstance = ShoppingCart.objects.get(user=request.user)
            detailserializer = ShoppingCartDetailSerializer(updatedinstance)
            return Response(detailserializer.data, status=status.HTTP_202_ACCEPTED)

        cartproduct = Product.objects.get(id=request.data["products"])
        itemset = Product.objects.filter(group_id=cartproduct.group_id, available=True)
        available_itemset = itemset.exclude(id__in=instance.products.values("id"))
        removable_itemset = instance.products.filter(group_id=cartproduct.group_id)
        amount = request.data["amount"]

        # front sends either a negative or a positive amount
        if amount > 0:
            if len(available_itemset) < amount:
                amount = len(available_itemset)
            for i in range(amount):
                instance.products.add(available_itemset[i])
        else:
            # if amount is negative, conversion to positive for iterating over removable_itemset
            amount *= -1
            if amount > len(removable_itemset):
                amount = len(removable_itemset)
            for i in range(amount):
                instance.products.remove(removable_itemset[i])

        updatedinstance = ShoppingCart.objects.get(user=request.user)
        detailserializer = ShoppingCartDetailSerializer(updatedinstance)
        return Response(detailserializer.data, status=status.HTTP_202_ACCEPTED)


class OrderListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


class OrderFilter(filters.FilterSet):
    STATUS_CHOICES = (
        ("Waiting", "Waiting"),
        ("Delivery", "Delivery"),
        ("Finished", "Finished"),
    )
    status = filters.ChoiceFilter(method="status_filter", choices=STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ["status"]

    def status_filter(self, queryset, name, value):
        return queryset.filter(Q(status__iexact=value))


class OrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderListPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["id"]
    filterset_class = OrderFilter

    @extend_schema(request=OrderRequestSerializer)
    def post(self, request, *args, **kwargs):
        user_id = request.data["user"]
        available_products_ids = product_availibility_check(user_id)
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.get(id=serializer.data["id"])
            for product_id in available_products_ids:
                order.products.add(product_id)
            updated_serializer = OrderSerializer(order).data
            subject = f"Tilaus {order.id}"
            message = "viesti"
            send_mail(
                subject=subject, message=message, settings=settings.EMAIL_HOST_USER
            )
            return Response(updated_serializer, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    @extend_schema(request=OrderDetailRequestSerializer)
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.products.clear()
        for product in request.data["products"]:
            instance.products.add(product)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class OrderSelfListView(ListAPIView):
    """View for returning logged in users own orders"""

    serializer_class = OrderSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        return Order.objects.filter(user=self.request.user)
