"""The bike rental views."""

import datetime
import math
import holidays

from django.core.files.base import ContentFile
from django.utils import timezone
from django_filters import rest_framework as filters

# from rest_framework.permissions import IsAdminUser
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter


from users.views import CustomJWTAuthentication

from drf_spectacular.utils import extend_schema_view, extend_schema

from bikes.models import (
    Bike,
    BikePackage,
    BikeRental,
    BikeStock,
    BikeType,
    BikeSize,
    BikeBrand,
)
from bikes.serializers import (
    BikeAvailabilityListSerializer,
    BikeAvailabilityListResponseSerializer,
    BikePackageSerializer,
    BikePackageListSerializer,
    BikeRentalSerializer,
    BikeSerializer,
    BikeStockListSerializer,
    BikeStockDetailSerializer,
    BikeRentalSchemaPostSerializer,
    BikeRentalSchemaResponseSerializer,
    BikeStockCreateSerializer,
    BikeStockSchemaCreateUpdateSerializer,
    BikeModelSerializer,
    BikeModelCreateSerializer,
    BikeModelSchemaResponseSerializer,
    MainBikeListSchemaSerializer,
    BikeTypeSerializer,
    BikeBrandSerializer,
    BikeSizeSerializer,
)

from products.serializers import PictureCreateSerializer


@extend_schema_view(
    post=extend_schema(
        request=BikeModelCreateSerializer, responses=BikeModelSchemaResponseSerializer
    )
)
class BikeModelListView(generics.ListCreateAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeModelSerializer

    def post(self, request, *args, **kwargs):
        for file in request.FILES.getlist("pictures[]"):
            ext = file.content_type.split("/")[1]
            pic_serializer = PictureCreateSerializer(
                data={
                    "picture_address": ContentFile(
                        file.read(), name=f"{timezone.now().timestamp()}.{ext}"
                    )
                }
            )
            pic_serializer.is_valid(raise_exception=True)
            pic_serializer.save()
            bikepicture = pic_serializer.data["id"]

        bikedata = request.data
        bikedata["picture"] = bikepicture
        serializer = BikeModelCreateSerializer(data=bikedata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=BikeModelCreateSerializer, responses=BikeModelSchemaResponseSerializer
    ),
    patch=extend_schema(exclude=True),
)
class BikeModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeModelSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        bikedata = request.data
        for file in request.FILES.getlist("pictures[]"):
            ext = file.content_type.split("/")[1]
            pic_serializer = PictureCreateSerializer(
                data={
                    "picture_address": ContentFile(
                        file.read(), name=f"{timezone.now().timestamp()}.{ext}"
                    )
                }
            )
            pic_serializer.is_valid(raise_exception=True)
            pic_serializer.save()
            bikepicture = pic_serializer.data["id"]
            bikedata["picture"] = bikepicture

        serializer = BikeModelCreateSerializer(instance, data=bikedata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@extend_schema_view(
    post=extend_schema(
        request=BikeStockCreateSerializer,
        responses=BikeStockSchemaCreateUpdateSerializer,
    )
)
class BikeStockListView(generics.ListCreateAPIView):
    queryset = BikeStock.objects.all()
    serializer_class = BikeStockListSerializer
    # permission_classes = [isAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = BikeStockCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=BikeStockCreateSerializer,
        responses=BikeStockSchemaCreateUpdateSerializer,
    ),
    patch=extend_schema(exclude=True),
)
class BikeStockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeStock.objects.all()
    serializer_class = BikeStockDetailSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BikeStockCreateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@extend_schema_view(
    get=extend_schema(responses=BikeAvailabilityListResponseSerializer),
)
class BikeAvailabilityList(generics.ListAPIView):
    queryset = BikeStock.objects.all()
    serializer_class = BikeAvailabilityListSerializer

    def list(self, request, *args, **kwargs):
        today = datetime.date.today()
        available_from = today + datetime.timedelta(days=7)
        available_to = today + datetime.timedelta(days=183)
        fin_holidays = holidays.FI()
        asd = self.get_queryset()
        serializer = self.get_serializer(asd, many=True)
        for bike in serializer.data:
            bike["available_from"] = available_from
            bike["available_to"] = available_to
            bike["rental_dates"] = []
            for rental in bike["rental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5 or end_date in fin_holidays:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str not in bike["rental_dates"]:
                        bike["rental_dates"].append(date_str)
                    date += datetime.timedelta(days=1)
            del bike["rental"]

        packageserializer = BikePackageSerializer(BikePackage.objects.all(), many=True)
        for package in packageserializer.data:
            package["rental_dates"] = []
            for rental in package["packagerental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5 or end_date in fin_holidays:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str not in package["rental_dates"]:
                        package["rental_dates"].append(date_str)
                    date += datetime.timedelta(days=1)
            del package["packagerental"]

        kekkedata = serializer.data + packageserializer.data

        return Response(kekkedata, status=status.HTTP_200_OK)


class MainBikeList(generics.ListAPIView):
    serializer_class = MainBikeListSchemaSerializer
    queryset = Bike.objects.none()

    def list(self, request, *args, **kwargs):
        today = datetime.date.today()
        available_from = today + datetime.timedelta(days=7)
        available_to = today + datetime.timedelta(days=183)
        fin_holidays = holidays.FI()

        bike_serializer = BikeSerializer(Bike.objects.all(), many=True)
        bike_package_serializer = BikePackageSerializer(
            BikePackage.objects.all(), many=True
        )

        for index, bike in enumerate(bike_serializer.data):
            max_available = 0
            unavailable = {}
            for bike in bike["stock"]:
                if bike["package_only"] is False:
                    max_available += 1
                    for rental in bike["rental"]:
                        start_date = datetime.datetime.fromisoformat(
                            rental["start_date"]
                        )
                        end_date = datetime.datetime.fromisoformat(rental["end_date"])
                        # We want to give the warehouse workers a business day to maintain the bikes, after the rental has ended
                        end_date += datetime.timedelta(days=1)
                        while end_date.weekday() >= 5 or end_date in fin_holidays:
                            end_date += datetime.timedelta(days=1)
                        date = start_date
                        while date <= end_date:
                            date_str = date.strftime("%d.%m.%Y")
                            if date_str in unavailable:
                                unavailable[date_str] = 1 + unavailable[date_str]
                            else:
                                unavailable[date_str] = 1
                            date += datetime.timedelta(days=1)
                else:
                    pass
            bike_serializer.data[index]["unavailable"] = unavailable
            bike_serializer.data[index]["max_available"] = max_available
            del bike_serializer.data[index]["stock"]

        for index, package in enumerate(bike_package_serializer.data):
            serializer_package = bike_package_serializer.data[index]
            serializer_package["type"] = "Paketti"
            serializer_package["unavailable"] = {}
            serializer_package["max_available"] = 1
            for packagerental in package["packagerental"]:
                start_date = datetime.datetime.fromisoformat(
                    packagerental["start_date"]
                )
                end_date = datetime.datetime.fromisoformat(packagerental["end_date"])
                # We want to give the warehouse workers a business day to maintain the bikes, after the rental has ended
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5 or end_date in fin_holidays:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str in unavailable:
                        serializer_package["unavailable"][date_str] = (
                            1 + serializer_package["unavailable"][date_str]
                        )
                    else:
                        serializer_package["unavailable"][date_str] = 1
                    date += datetime.timedelta(days=1)
            del bike_package_serializer.data[index]["packagerental"]

        return Response(
            {
                "date_info": {
                    "available_from": available_from,
                    "available_to": available_to,
                },
                "bikes": bike_serializer.data,
                "packages": bike_package_serializer.data,
            }
        )


class BikeRentalPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


class BikeRentalFilter(filters.FilterSet):
    state = filters.MultipleChoiceFilter(choices=BikeRental.StateChoices.choices)

    class Meta:
        model = BikeRental
        fields = ["state"]


@extend_schema_view(
    get=extend_schema(responses=BikeRentalSchemaResponseSerializer),
    post=extend_schema(
        request=BikeRentalSchemaPostSerializer,
        responses=BikeRentalSchemaResponseSerializer,
    ),
)
class RentalListView(generics.ListCreateAPIView):
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    pagination_class = BikeRentalPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["id", "state", "start_date", "end_date"]
    ordering = ["-start_date"]
    filterset_class = BikeRentalFilter

    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer

    def post(self, request, *args, **kwargs):
        request_start_date = datetime.datetime.fromisoformat(request.data["start_date"])
        request_end_date = datetime.datetime.fromisoformat(request.data["end_date"])

        bikerentalserializer = BikeAvailabilityListSerializer(
            BikeStock.objects.all(), many=True
        )
        for bike in bikerentalserializer.data:
            bike["rental_dates"] = []
            for rental in bike["rental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str not in bike["rental_dates"]:
                        bike["rental_dates"].append(date_str)
                    date += datetime.timedelta(days=1)
            del bike["rental"]
        unavailable_dates = {}
        for bikedata in bikerentalserializer.data:
            unavailable_dates[bikedata["id"]] = bikedata["rental_dates"]
        print(unavailable_dates)

        packageserializer = BikePackageSerializer(BikePackage.objects.all(), many=True)
        for package in packageserializer.data:
            package["rental_dates"] = []
            for rental in package["packagerental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str not in package["rental_dates"]:
                        package["rental_dates"].append(date_str)
                    date += datetime.timedelta(days=1)
            del package["packagerental"]
        package_unavailable_dates = {}
        for packagedata in packageserializer.data:
            package_unavailable_dates[packagedata["id"]] = packagedata["rental_dates"]
        print(package_unavailable_dates)

        instance = request.data
        bikes_list = []
        packages_list = []
        for rental_item in request.data["bike_stock"]:
            if rental_item.startswith("package"):
                package = rental_item.split("-", 1)[1]
                print(package)
                packages_list.append(package)

            else:
                available_bikes = BikeStock.objects.filter(
                    bike=rental_item, package_only=False, state="AVAILABLE"
                )
                for bike_id in available_bikes:
                    check_date = request_start_date
                    if bike_id.id in unavailable_dates.keys():
                        while check_date <= request_end_date:
                            if (
                                check_date.strftime("%d.%m.%Y")
                                in unavailable_dates[bike_id.id]
                            ):
                                available_bikes = available_bikes.exclude(id=bike_id.id)
                            check_date += datetime.timedelta(days=1)
                amount = request.data["bike_stock"][rental_item]
                for bike in range(amount):
                    bikes_list.append(available_bikes[bike].id)
        instance["bike_stock"] = bikes_list
        instance["packages"] = packages_list
        instance["user"] = self.request.user.id
        serializer = BikeRentalSerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(responses=BikeRentalSchemaResponseSerializer),
    put=extend_schema(
        responses=BikeRentalSchemaResponseSerializer,
    ),
    patch=extend_schema(exclude=True),
)
class RentalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer


class BikePackageListView(generics.ListCreateAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageListSerializer

    def post(self, request, *args, **kwargs):
        package_bikes = []
        for bikeid in request.data["bike_stock"]:
            bikeobject = BikeStock.objects.get(id=bikeid)
            if bikeobject.package is None:
                package_bikes.append(bikeid)
            request.data["bike_stock"] = package_bikes
        serializer = BikePackageListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for bike in serializer.validated_data["bike_stock"]:
            bike.package_only = True
            bike.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikePackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        instance_bikes = instance.bike_stock.values_list("id", flat=True)
        package_bikes = []
        for bikeid in request.data["bike_stock"]:
            if bikeid not in instance_bikes:
                bikeobject = BikeStock.objects.get(id=bikeid)
                if bikeobject.package is None:
                    package_bikes.append(bikeid)
            else:
                package_bikes.append(bikeid)
        request.data["bike_stock"] = package_bikes

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        for bike in serializer.validated_data["bike_stock"]:
            bike.package_only = True
            bike.save()

        self.perform_update(serializer)

        for bike in instance_bikes:
            if bike not in package_bikes:
                removed_bike = BikeStock.objects.get(id=bike)
                removed_bike.package_only = False
                removed_bike.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        removable_package = self.get_object()
        for bike in removable_package.bike_stock.all():
            bike.package_only = False
            bike.save()
        removable_package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BikeTypeListView(generics.ListCreateAPIView):
    queryset = BikeType.objects.all()
    serializer_class = BikeTypeSerializer


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeType.objects.all()
    serializer_class = BikeTypeSerializer


class BikeBrandListView(generics.ListCreateAPIView):
    queryset = BikeBrand.objects.all()
    serializer_class = BikeBrandSerializer


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeBrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeBrand.objects.all()
    serializer_class = BikeBrandSerializer


class BikeSizeListView(generics.ListCreateAPIView):
    queryset = BikeSize.objects.all()
    serializer_class = BikeSizeSerializer


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeSizeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeSize.objects.all()
    serializer_class = BikeSizeSerializer
