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

        try:
            parentcheck = Category.objects.get(id=instance["parent"])
            if parentcheck.level >= 2:
                return Response("Maximum category level(2) exceeded",status=status.HTTP_400_BAD_REQUEST)
        except:
            instance["parent"] == None
        
        serializer = CategorySerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
