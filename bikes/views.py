"""The bike rental views."""

import datetime
import math

# from rest_framework.permissions import IsAdminUser
from rest_framework import generics, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema_view, extend_schema

from bikes.models import Bike, BikePackage, BikeRental, BikeStock, BikeAmount, BikeType, BikeSize, BikeBrand
from bikes.serializers import (
    BikeAmountListSerializer,
    BikePackageSerializer,
    BikePackageSchemaResponseSerializer,
    BikePackageCreateResponseSerializer,
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

@extend_schema_view(
    post=extend_schema(
        request=BikeModelCreateSerializer,
        responses=BikeModelSchemaResponseSerializer
    )
)
class BikeModelListView(generics.ListCreateAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeModelSerializer

    def post(self,request, *args, **kwargs):
        serializer = BikeModelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=BikeModelCreateSerializer,
        responses=BikeModelSchemaResponseSerializer
    ),
    patch=extend_schema(
        exclude=True
    )
)
class BikeModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeModelSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BikeModelCreateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@extend_schema_view(
    post=extend_schema(
        request=BikeStockCreateSerializer,
        responses=BikeStockSchemaCreateUpdateSerializer
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
        responses=BikeStockSchemaCreateUpdateSerializer
    ),
    patch=extend_schema(
        exclude=True
    )
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


class MainBikeList(generics.ListAPIView):
    serializer_class = MainBikeListSchemaSerializer
    queryset = Bike.objects.none()

    def list(self, request, *args, **kwargs):
        today = datetime.date.today()
        available_from = today + datetime.timedelta(days=7)
        available_to = today + datetime.timedelta(days=183)

        bike_serializer = BikeSerializer(Bike.objects.all(), many=True)
        bike_package_serializer = BikePackageSerializer(
            BikePackage.objects.all(), many=True
        )

        for index, bike in enumerate(bike_serializer.data):
            package_only_count = 0
            unavailable = {}
            package_only_unavailable = {}
            for bike in bike["stock"]:
                if bike["package_only"] is True:
                    package_only_count += 1
                    for rental in bike["rental"]:
                        start_date = datetime.datetime.fromisoformat(
                            rental["start_date"]
                        )
                        end_date = datetime.datetime.fromisoformat(rental["end_date"])
                        # We want to give the warehouse workers a business day to maintain the bikes, after the rental has ended
                        end_date += datetime.timedelta(days=1)
                        while end_date.weekday() >= 5:
                            end_date += datetime.timedelta(days=1)
                        date = start_date
                        while date <= end_date:
                            date_str = date.strftime("%d.%m.%Y")
                            if date_str in package_only_unavailable:
                                package_only_unavailable[date_str] = (
                                    1 + package_only_unavailable[date_str]
                                )
                            else:
                                package_only_unavailable[date_str] = 1
                            date += datetime.timedelta(days=1)
                else:
                    for rental in bike["rental"]:
                        start_date = datetime.datetime.fromisoformat(
                            rental["start_date"]
                        )
                        end_date = datetime.datetime.fromisoformat(rental["end_date"])
                        # We want to give the warehouse workers a business day to maintain the bikes, after the rental has ended
                        end_date += datetime.timedelta(days=1)
                        while end_date.weekday() >= 5:
                            end_date += datetime.timedelta(days=1)
                        date = start_date
                        while date <= end_date:
                            date_str = date.strftime("%d.%m.%Y")
                            if date_str in unavailable:
                                unavailable[date_str] = 1 + unavailable[date_str]
                            else:
                                unavailable[date_str] = 1
                            date += datetime.timedelta(days=1)
            bike_serializer.data[index]["unavailable"] = unavailable
            bike_serializer.data[index]["package_only_count"] = package_only_count
            bike_serializer.data[index][
                "package_only_unavailable"
            ] = package_only_unavailable
            del bike_serializer.data[index]["stock"]

        for index, package in enumerate(bike_package_serializer.data):
            serializer_package = bike_package_serializer.data[index]
            serializer_package["type"] = "Paketti"
            serializer_package["unavailable"] = {}
            serializer_package["brand"] = None
            serializer_package["color"] = None
            max_available = None
            for bike in package["bikes"]:
                bike_object = Bike.objects.get(id=bike["bike"])
                if "size" in serializer_package:
                    serializer_package[
                        "size"
                    ] = f"{serializer_package['size']} & {bike_object.size.name}"
                else:
                    serializer_package["size"] = bike_object.size.name
                bike_object_serializer = BikeSerializer(bike_object)
                bike_max_available = math.floor(
                    bike_object_serializer.data["max_available"] / bike["amount"]
                )
                if max_available is None:
                    max_available = bike_max_available
                else:
                    max_available = min(max_available, bike_max_available)
            serializer_package["max_available"] = max_available

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


@extend_schema_view(
    get=extend_schema(
        responses=BikeRentalSchemaResponseSerializer
    ),
    post=extend_schema(
        request=BikeRentalSchemaPostSerializer,
        responses=BikeRentalSchemaResponseSerializer
    )
)
class RentalListView(generics.ListCreateAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer

    def post(self, request, *args, **kwargs):
        instance = request.data
        bikes_list = []
        for rental_item in request.data["bike_stock"]:
            if rental_item.startswith("package"):
                package = BikePackage.objects.get(
                    id=rental_item.split("-", 1)[1]
                ).bikes.values("id", "amount")
                packageamount = request.data["bike_stock"][rental_item]
                for packageitem in package:
                    amount = packageamount * packageitem["amount"]
                    available_bikes = BikeStock.objects.filter(
                        bike=packageitem["id"]
                    ).order_by("-package_only", "id")
                    for bike in range(amount):
                        bikes_list.append(available_bikes[bike].id)
            else:
                available_bikes = BikeStock.objects.filter(
                    bike=rental_item, package_only=False
                )
                amount = request.data["bike_stock"][rental_item]
                for bike in range(amount):
                    bikes_list.append(available_bikes[bike].id)
        instance["bike_stock"] = bikes_list
        serializer = BikeRentalSerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        responses=BikeRentalSchemaResponseSerializer
    ),
)
class RentalDetailView(generics.RetrieveAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer


class BikeAmountListView(generics.ListAPIView):
    queryset = BikeAmount.objects.all()
    serializer_class = BikeAmountListSerializer


@extend_schema_view(
    get=extend_schema(
        responses=BikePackageSchemaResponseSerializer()
    ),
    post=extend_schema(
        request=BikePackageCreateResponseSerializer(),
        responses=BikePackageSchemaResponseSerializer()
    ),
)
class BikePackageListView(generics.ListCreateAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageSerializer


@extend_schema_view(
    get=extend_schema(
        responses=BikePackageSchemaResponseSerializer()
    ),
    put=extend_schema(
        responses=BikePackageSchemaResponseSerializer()
    ),
    patch=extend_schema(
        exclude=True
    ),
)
class BikePackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageSerializer


class BikeTypeListView(generics.ListCreateAPIView):
    queryset = BikeType.objects.all()
    serializer_class = BikeTypeSerializer


class BikeBrandListView(generics.ListCreateAPIView):
    queryset = BikeBrand.objects.all()
    serializer_class = BikeBrandSerializer


class BikeSizeListView(generics.ListCreateAPIView):
    queryset = BikeSize.objects.all()
    serializer_class = BikeSizeSerializer
