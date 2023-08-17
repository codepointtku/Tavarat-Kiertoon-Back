from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.authenticate import CustomJWTAuthentication
from users.permissions import HasGroupPermission

from .models import Bulletin
from .serializers import BulletinResponseSerializer, BulletinSerializer


# Create your views here.
@extend_schema_view(
    get=extend_schema(responses=BulletinResponseSerializer),
    post=extend_schema(responses=BulletinResponseSerializer),
)
class BulletinListView(ListCreateAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [HasGroupPermission]
    required_groups = {
        "POST": ["admin_group", "user_group"],
    }


@extend_schema_view(
    get=extend_schema(responses=BulletinResponseSerializer),
    put=extend_schema(responses=BulletinResponseSerializer),
    patch=extend_schema(exclude=True),
)
class BulletinDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [HasGroupPermission]
    required_groups = {
        "PUT": ["admin_group", "user_group"],
        "PATCH": ["admin_group", "user_group"],
        "DELETE": ["admin_group", "user_group"],
    }
