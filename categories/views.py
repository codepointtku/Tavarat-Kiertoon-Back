from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category
from .serializers import CategorySerializer, CategoryTreeSerializer


# Create your views here.
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        instance = request.data

        try:
            parentcheck = Category.objects.get(id=instance["parent"])
            if parentcheck.level >= 2:
                return Response(
                    "Maximum category level(2) exceeded",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            instance["parent"] == None

        serializer = CategorySerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryTreeView(APIView):
    """Returns all category ids as keys and all level 2 child categories of that category as list"""

    queryset = Category.objects.all()

    @extend_schema(
        responses=CategoryTreeSerializer,
        examples=[
            OpenApiExample("Example 1", description="longer description", value=5)
        ],
    )
    def get(self, request, *args, **kwargs):
        category_tree = {
            c.id: [c.id for c in c.get_descendants(include_self=True).filter(level=2)]
            for c in self.queryset.all()
        }
        return Response(category_tree)
