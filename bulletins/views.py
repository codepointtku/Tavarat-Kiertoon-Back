from drf_spectacular.utils import extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Bulletin
from .serializers import BulletinResponseSerializer, BulletinSerializer


# Create your views here.
class BulletinListView(ListCreateAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]

    @extend_schema(responses=BulletinResponseSerializer)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(responses=BulletinResponseSerializer)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BulletinDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer

    @extend_schema(responses=BulletinResponseSerializer)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(responses=BulletinResponseSerializer)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], exclude=True)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
