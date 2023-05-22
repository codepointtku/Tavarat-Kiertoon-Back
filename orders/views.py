from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
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

from products.models import Product, ProductItem
from users.models import CustomUser
from users.views import CustomJWTAuthentication

from .models import Order, ShoppingCart
from .serializers import (
    OrderDetailRequestSerializer,
    OrderDetailResponseSerializer,
    OrderDetailSerializer,
    OrderRequestSerializer,
    OrderResponseSerializer,
    OrderSerializer,
    ShoppingCartDetailRequestSerializer,
    ShoppingCartDetailSerializer,
    ShoppingCartResponseSerializer,
    ShoppingCartSerializer,
)

# Create your views here.


@extend_schema_view(
    get=extend_schema(responses=ShoppingCartResponseSerializer),
    post=extend_schema(responses=ShoppingCartResponseSerializer),
)
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


@extend_schema_view(
    put=extend_schema(request=ShoppingCartDetailRequestSerializer),
    patch=extend_schema(exclude=True),
)
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

    def put(self, request, *args, **kwargs):
        try:
            instance = ShoppingCart.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response("Shopping cart for this user does not exist")
        # if amount is -1, clear users ShoppingCart
        if request.data["amount"] == -1:
            instance.product_items.clear()
            updatedinstance = ShoppingCart.objects.get(user=request.user)
            detailserializer = ShoppingCartDetailSerializer(updatedinstance)
            return Response(detailserializer.data, status=status.HTTP_202_ACCEPTED)

        changeable_product = ProductItem.objects.get(id=request.data["product_items"])
        itemset = ProductItem.product_set.filter(available=True)
        available_itemset = itemset.exclude(id__in=instance.product_items.values("id"))
        removable_itemset = instance.product_items.filter(
            product=changeable_product.product
        )
        amount = request.data["amount"]

        # comparing amount to number of product_items already in shoppingcart, proceeding accordingly
        if len(removable_itemset) < amount:
            amount -= len(removable_itemset)
            if len(available_itemset) < amount:
                amount = len(available_itemset)
            for i in range(amount):
                instance.product_items.add(available_itemset[i])

        else:
            amount -= len(removable_itemset)
            amount *= -1
            for i in range(amount):
                instance.product_items.remove(removable_itemset[i])

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


@extend_schema_view(
    get=extend_schema(responses=OrderResponseSerializer),
    post=extend_schema(
        request=OrderRequestSerializer, responses=OrderResponseSerializer
    ),
)
class OrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderListPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]
    filterset_class = OrderFilter
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.get(id=serializer.data["id"])
            shopping_cart = ShoppingCart.objects.get(user=user.id)
            for productitem in shopping_cart.product_items.all():
                order.product_items.add(productitem)
            subject = f"Tavarat Kiertoon tilaus {order.id}"
            message = (
                "Hei!\n"
                "Vastaanotimme tilauksesi ja tilaus pyrimme toimittamaan sen 1-2 viikon sisällä\n"
                f"Tilausnumeronne on {order.id}.\n\n"
                "Terveisin Tavarat kieroon väki!"
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(responses=OrderDetailResponseSerializer),
    put=extend_schema(
        request=OrderDetailRequestSerializer, responses=OrderDetailResponseSerializer
    ),
    patch=extend_schema(exclude=True),
)
class OrderDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.product_items.clear()
        for product in request.data["product_items"]:
            instance.product_items.add(product)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@extend_schema_view(get=extend_schema(responses=OrderDetailResponseSerializer))
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
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)
