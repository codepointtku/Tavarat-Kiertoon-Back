from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer

# Create your views here.
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        instance = request.data
        levelchecker = Category.objects.filter(id=instance["parent"]).values("level")
        level = list(levelchecker)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid()and level[0]["level"] < 2:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
