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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product, ProductItem, ProductItemLogEntry
from users.permissions import HasGroupPermission
from users.views import CustomJWTAuthentication

from .models import Order, OrderEmailRecipient, ShoppingCart
from .serializers import (
    OrderDetailRequestSerializer,
    OrderDetailResponseSerializer,
    OrderDetailSerializer,
    OrderEmailRecipientSerializer,
    OrderRequestSerializer,
    OrderResponseSerializer,
    OrderSerializer,
    ShoppingCartDetailRequestSerializer,
    ShoppingCartDetailResponseSerializer,
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

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group", "user_group"],
        "POST": ["admin_group", "user_group"],
    }

    def post(self, request):
        serializer = ShoppingCartSerializer(data=request.data)
        if serializer.is_valid():
            if len(ShoppingCart.objects.filter(user=request.data["user"])) != 0:
                ShoppingCart.objects.filter(user=request.data["user"]).delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(responses=ShoppingCartDetailResponseSerializer),
    put=extend_schema(
        request=ShoppingCartDetailRequestSerializer,
        responses=ShoppingCartDetailResponseSerializer,
    ),
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

    permission_classes = [HasGroupPermission]
    required_groups = {
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

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
            log_entry = ProductItemLogEntry.objects.create(
                action=ProductItemLogEntry.ActionChoices.CART_REMOVE, user=request.user
            )
            for product_item in instance.product_items.all():
                product_item.log_entries.add(log_entry)
                product_item.available = True
                product_item.status = "Available"
                product_item.save()
            instance.product_items.clear()
            instance.save()
            # updatedinstance = ShoppingCart.objects.get(user=request.user)
            # detailserializer = ShoppingCartDetailSerializer(updatedinstance)
            return Response(status=status.HTTP_202_ACCEPTED)

        changeable_product = Product.objects.get(id=request.data["product"])
        itemset = ProductItem.objects.filter(product=changeable_product, available=True)
        available_itemset = itemset.exclude(id__in=instance.product_items.values("id"))
        removable_itemset = instance.product_items.filter(product=changeable_product)
        amount = request.data["amount"]

        # comparing amount to number of product_items already in shoppingcart, proceeding accordingly
        if len(removable_itemset) < amount:
            log_entry = ProductItemLogEntry.objects.create(
                action=ProductItemLogEntry.ActionChoices.CART_ADD, user=request.user
            )
            amount -= len(removable_itemset)
            if len(available_itemset) < amount:
                amount = len(available_itemset)
            for i in range(amount):
                instance.product_items.add(available_itemset[i])
                available_itemset[i].log_entries.add(log_entry)
                available_itemset[i].available = False
                available_itemset[i].status = "In cart"
                available_itemset[i].save()
            instance.save()

        else:
            log_entry = ProductItemLogEntry.objects.create(
                action=ProductItemLogEntry.ActionChoices.CART_REMOVE, user=request.user
            )
            amount -= len(removable_itemset)
            amount *= -1
            for i in range(amount):
                instance.product_items.remove(removable_itemset[i])
                removable_itemset[i].log_entries.add(log_entry)
                removable_itemset[i].available = True
                removable_itemset[i].status = "Available"
                removable_itemset[i].save()
            instance.save()

        # updatedinstance = ShoppingCart.objects.get(user=request.user)
        # detailserializer = ShoppingCartDetailSerializer(updatedinstance)
        return Response(status=status.HTTP_202_ACCEPTED)


class OrderListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


class OrderFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = ["status"]

    def status_filter(self, queryset, name, value):
        return queryset.filter(Q(status__iexact=value))


class UserOrderFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=Order.StatusChoices.choices)

    class Meta:
        model = Order
        fields = ["status"]


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

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["storage_group", "user_group"],
        "POST": ["user_group"],
    }

    def post(self, request, *args, **kwargs):
        user = request.user
        shopping_cart = ShoppingCart.objects.get(user=user.id)
        serializer = OrderSerializer(data=request.data)
        if shopping_cart.product_items.count() < 1:
            return Response("Order has no products", status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.get(id=serializer.data["id"])
            order.user = user
            log_entry = ProductItemLogEntry.objects.create(
                action=ProductItemLogEntry.ActionChoices.ORDER, user=user
            )
            for product_item in shopping_cart.product_items.all():
                order.product_items.add(product_item)
                product_item.log_entries.add(log_entry)
                product_item.status = "Unavailable"
                product_item.save()
            shopping_cart.product_items.clear()

            # Email for user who submitted order
            subject = f"Tavarat Kiertoon tilaus {order.id}"
            message = (
                "Hei!\n\n"
                "Vastaanotimme tilauksesi. Pyrimme toimittamaan sen 1-2 viikon sisällä\n"
                f"Tilausnumeronne on {order.id}.\n\n"
                "Terveisin Tavarat kiertoon väki!"
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            # Email for all OrderEmailRecipients notifying about new order
            message = (
                "Hei\n\n"
                f"Käyttäjä {user.username} teki tilauksen Tavarat kiertoon järjestelmään.\n"
                f"Linkki tilaukseen http://localhost:3000/varasto/tilaus/{order.id}/"
            )
            recipients = [
                recipient.email for recipient in OrderEmailRecipient.objects.all()
            ]
            recipients.append(settings.DEFAULT_EMAIL)
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)
            serializer = OrderSerializer(order)
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
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["storage_group", "user_group"],
        "PUT": ["admin_group", "user_group"],
        "PATCH": ["admin_group", "user_group"],
        "DELETE": ["admin_group", "user_group"],
    }

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        user = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        remove = 0
        add = 0
        for product_item in instance.product_items.values("id"):
            if product_item["id"] not in request.data["product_items"]:
                if remove == 0:
                    remove = 1
                    log_remove = ProductItemLogEntry.objects.create(
                        action=ProductItemLogEntry.ActionChoices.ORDER_REMOVE, user=user
                    )
                product_item_object = ProductItem.objects.get(id=product_item["id"])
                product_item_object.available = True
                product_item_object.status = "Available"
                product_item_object.save()
                instance.product_items.remove(product_item["id"])
                product_item_object.log_entries.add(log_remove)
        for product_item in request.data["product_items"]:
            if product_item not in instance.product_items.values_list("id", flat=True):
                product_item_object = ProductItem.objects.get(id=product_item)
                if product_item_object.available == True:
                    if add == 0:
                        add = 1
                        log_add = ProductItemLogEntry.objects.create(
                            action=ProductItemLogEntry.ActionChoices.ORDER_ADD,
                            user=user,
                        )
                    product_item_object.available = False
                    product_item_object.status = "Unavailable"
                    product_item_object.save()
                    instance.product_items.add(product_item)
                    product_item_object.log_entries.add(log_add)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status == "Finished":
            return Response(
                "Cant delete finished orders", status=status.HTTP_403_FORBIDDEN
            )
        log_entry = ProductItemLogEntry.objects.create(
            action=ProductItemLogEntry.ActionChoices.ORDER_REMOVE, user=request.user
        )
        for product_item in order.product_items.all():
            product_item.available = True
            product_item.status = "Available"
            product_item.log_entries.add(log_entry)
            product_item.save()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderSelfListView(ListAPIView):
    """View for returning logged in users own orders"""

    serializer_class = OrderDetailResponseSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
    }

    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["creation_date", "status"]
    ordering = ["-creation_date"]
    filterset_class = UserOrderFilter

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)


class OrderEmailRecipientListView(ListCreateAPIView):
    serializer_class = OrderEmailRecipientSerializer
    queryset = OrderEmailRecipient.objects.all()

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "POST": ["admin_group", "user_group"],
    }


@extend_schema_view(patch=extend_schema(exclude=True))
class OrderEmailRecipientDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderEmailRecipientSerializer
    queryset = OrderEmailRecipient.objects.all()

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group", "user_group"],
        "PUT": ["admin_group", "user_group"],
        "PATCH": ["admin_group", "user_group"],
        "DELETE": ["admin_group", "user_group"],
    }
