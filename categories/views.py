from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.authenticate import CustomJWTAuthentication
from users.permissions import HasGroupPermission

from .models import Category
from .serializers import (
    CategoryResponseSerializer,
    CategorySerializer,
    CategoryTreeSerializer,
)


# Create your views here.
@extend_schema_view(
    get=extend_schema(responses=CategoryResponseSerializer),
    post=extend_schema(responses=CategoryResponseSerializer),
)
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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

    def post(self, request, *args, **kwargs):
        instance = request.data
        try:
            parentcheck = Category.objects.get(id=instance["parent"])
            if parentcheck.level >= 2:
                return Response(
                    "Maximum category level(2) exceeded",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:  # What error this should catch? Maybe its good to specify that error.
            instance["parent"] == None

        serializer = CategorySerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(responses=CategoryResponseSerializer),
    put=extend_schema(responses=CategoryResponseSerializer),
    patch=extend_schema(exclude=True),
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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


class CategoryTreeView(APIView):
    """Returns all category ids as keys and all level 2 child categories of that category as list"""

    queryset = Category.objects.all()

    @extend_schema(
        responses=CategoryTreeSerializer,
        examples=[
            OpenApiExample(
                "Example 1",
                description="Keys are category ids, and values are list of all lvl 2 child category ids of that category",
                value={
                    "1": [3, 4, 6, 7],
                    "2": [3, 4],
                    "3": [3],
                    "4": [4],
                    "5": [6, 7],
                    "6": [6],
                    "7": [7],
                    "8": [10],
                    "9": [10],
                    "10": [10],
                },
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        category_tree = {
            c.id: [c.id for c in c.get_descendants(include_self=True).filter(level=2)]
            for c in self.queryset.all()
        }
        return Response(category_tree)
