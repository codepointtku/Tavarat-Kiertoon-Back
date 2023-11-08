"""The bike rental views."""

import datetime
import math

import holidays
from django.core.files.base import ContentFile
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view

# from rest_framework.permissions import IsAdminUser
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from bikes.models import (
    Bike,
    BikeAmount,
    BikeBrand,
    BikePackage,
    BikeRental,
    BikeSize,
    BikeStock,
    BikeType,
    BikeSize,
    BikeBrand,
    BikeTrailer,
    BikeTrailerModel,
)
from bikes.serializers import (
    BikeAmountListSerializer,
    BikeAvailabilityListSerializer,
    BikeBrandSerializer,
    BikeModelCreateSerializer,
    BikeModelSchemaResponseSerializer,
    BikeModelSerializer,
    BikePackageCreateResponseSerializer,
    BikePackageSchemaResponseSerializer,
    BikePackageSerializer,
    BikeRentalDepthSerializer,
    BikeRentalSchemaPostSerializer,
    BikeRentalSchemaResponseSerializer,
    BikeRentalSerializer,
    BikeSerializer,
    BikeSizeSerializer,
    BikeStockCreateSerializer,
    BikeStockDetailSerializer,
    BikeStockListSerializer,
    BikeStockSchemaCreateUpdateSerializer,
    BikeTypeSerializer,
    MainBikeListSchemaSerializer,
    PictureCreateSerializer,
    BikeTrailerSerializer,
    BikeTrailerModelSerializer,
    BikeTrailerMainSerializer,
    BikeTrailerAvailabilityListSerializer,
)
from users.permissions import HasGroupPermission
from users.views import CustomJWTAuthentication


@extend_schema_view(
    post=extend_schema(
        request=BikeModelCreateSerializer, responses=BikeModelSchemaResponseSerializer
    )
)
class BikeModelListView(generics.ListCreateAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeModelSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }

    def post(self, request, *args, **kwargs):
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

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "UPDATE": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }

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

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }

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

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "UPDATE": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BikeStockCreateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class MainBikeList(generics.ListAPIView):
    serializer_class = MainBikeListSchemaSerializer
    queryset = Bike.objects.none()

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "user_group"],
        "LIST": ["bicycle_group", "user_group"],
    }

    def list(self, request, *args, **kwargs):
        today = datetime.date.today()
        available_from = today + datetime.timedelta(days=7)
        available_to = today + datetime.timedelta(days=183)
        fin_holidays = holidays.FI()

        bike_serializer = BikeSerializer(Bike.objects.all(), many=True)
        bike_package_serializer = BikePackageSerializer(
            BikePackage.objects.all(), many=True
        )
        trailer_serializer = BikeTrailerMainSerializer(
            BikeTrailerModel.objects.all(), many=True
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
                        while end_date.weekday() >= 5 or end_date in fin_holidays:
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
                if bike["amount"] == 0:
                    bike_max_available = bike["amount"]
                else:
                    bike_max_available = math.floor(
                        bike_object_serializer.data["max_available"] / bike["amount"]
                    )
                if max_available is None:
                    max_available = bike_max_available
                else:
                    max_available = min(max_available, bike_max_available)
            serializer_package["max_available"] = max_available

        for index, trailer in enumerate(trailer_serializer.data):
            unavailable = {}
            for trailer in trailer["trailer"]:
                for rental in trailer["trailer_rental"]:
                    start_date = datetime.datetime.fromisoformat(rental["start_date"])
                    end_date = datetime.datetime.fromisoformat(rental["end_date"])
                    # We want to give the warehouse workers a business day to maintain the trailers, after the rental has ended
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
            trailer_serializer.data[index]["unavailable"] = unavailable
            del trailer_serializer.data[index]["trailer"]

        return Response(
            {
                "date_info": {
                    "available_from": available_from,
                    "available_to": available_to,
                },
                "bikes": bike_serializer.data,
                "packages": bike_package_serializer.data,
                "trailers": trailer_serializer.data,
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

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "user_group"],
    }

    pagination_class = BikeRentalPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["id", "state", "start_date", "end_date"]
    ordering = ["-start_date"]
    filterset_class = BikeRentalFilter

    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer

    def post(self, request, *args, **kwargs):

        postserializer = BikeRentalSchemaPostSerializer(data=request.data)
        if postserializer.is_valid():
            request_start_date = datetime.datetime.fromisoformat(request.data["start_date"])
            request_end_date = datetime.datetime.fromisoformat(request.data["end_date"])


        bikerentalserializer = BikeAvailabilityListSerializer(
            BikeStock.objects.all(), many=True
        )
        trailer_rental_serializer = BikeTrailerAvailabilityListSerializer(
            BikeTrailer.objects.all(), many=True
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

        for trailer in trailer_rental_serializer.data:
            trailer["rental_dates"] = []
            for rental in trailer["trailer_rental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                end_date += datetime.timedelta(days=1)
                while end_date.weekday() >= 5:
                    end_date += datetime.timedelta(days=1)
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str not in trailer["rental_dates"]:
                        trailer["rental_dates"].append(date_str)
                    date += datetime.timedelta(days=1)
            del trailer["trailer_rental"]
        trailer_unavailable_dates = {}
        for trailerdata in trailer_rental_serializer.data:
            trailer_unavailable_dates[trailerdata["id"]] = trailerdata["rental_dates"]

        instance = request.data
        bikes_list = []
        for rental_item in request.data["bike_stock"]:
            if rental_item.startswith("package"):
                package = BikePackage.objects.get(
                    id=rental_item.split("-", 1)[1]
                ).bikes.values("bike", "amount")
                packageamount = request.data["bike_stock"][rental_item]
                for packageitem in package:
                    amount = packageamount * packageitem["amount"]
                    available_bikes = (
                        BikeStock.objects.filter(
                            bike=packageitem["bike"], state="AVAILABLE"
                        )
                        .order_by("-package_only", "id")
                        .exclude(id__in=bikes_list)
                    )
                    for bike_id in available_bikes:
                        check_date = request_start_date
                        if bike_id.id in unavailable_dates.keys():
                            while check_date <= request_end_date:
                                if (
                                    check_date.strftime("%d.%m.%Y")
                                    in unavailable_dates[bike_id.id]
                                ):
                                    available_bikes = available_bikes.exclude(
                                        id=bike_id.id
                                    )
                                check_date += datetime.timedelta(days=1)
                    for bike in range(amount):
                        bikes_list.append(available_bikes[bike].id)

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
            instance["user"] = self.request.user.id

        print(request.data)
        if "bike_trailer" in request.data:
            trailers = BikeTrailer.objects.filter(
                trailer_type=request.data["bike_trailer"]
            )
            for trailer in trailers:
                check_date = request_start_date
                if trailer.id in trailer_unavailable_dates.keys():
                    while check_date <= request_end_date:
                        if (
                            check_date.strftime("%d.%m.%Y")
                            in trailer_unavailable_dates[trailer.id]
                        ):
                            trailers = trailers.exclude(id=trailer.id)
                        check_date += datetime.timedelta(days=1)

            if trailers.exists():
                instance["bike_trailer"] = trailers[0].id
            else:
                instance["bike_trailer"] = None

            serializer = BikeRentalSerializer(data=instance)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(postserializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(responses=BikeRentalDepthSerializer),
    put=extend_schema(
        responses=BikeRentalSchemaResponseSerializer,
    ),
    patch=extend_schema(exclude=True),
)
class RentalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BikeRentalDepthSerializer(instance)
        return Response(serializer.data)


class BikeAmountListView(generics.ListAPIView):
    queryset = BikeAmount.objects.all()
    serializer_class = BikeAmountListSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
    }


@extend_schema_view(
    get=extend_schema(responses=BikePackageSchemaResponseSerializer()),
    post=extend_schema(
        request=BikePackageCreateResponseSerializer(),
        responses=BikePackageSchemaResponseSerializer(),
    ),
)
class BikePackageListView(generics.ListCreateAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }


@extend_schema_view(
    get=extend_schema(responses=BikePackageSchemaResponseSerializer()),
    put=extend_schema(responses=BikePackageSchemaResponseSerializer()),
    patch=extend_schema(exclude=True),
)
class BikePackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikePackage.objects.all()
    serializer_class = BikePackageSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }


class BikeTypeListView(generics.ListCreateAPIView):
    queryset = BikeType.objects.all()
    serializer_class = BikeTypeSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeType.objects.all()
    serializer_class = BikeTypeSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }


class BikeBrandListView(generics.ListCreateAPIView):
    queryset = BikeBrand.objects.all()
    serializer_class = BikeBrandSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeBrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeBrand.objects.all()
    serializer_class = BikeBrandSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }


class BikeSizeListView(generics.ListCreateAPIView):
    queryset = BikeSize.objects.all()
    serializer_class = BikeSizeSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "POST": ["bicycle_group", "admin_group", "user_group"],
    }


@extend_schema_view(
    patch=extend_schema(exclude=True),
)
class BikeSizeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeSize.objects.all()
    serializer_class = BikeSizeSerializer

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["bicycle_group", "admin_group", "user_group"],
        "PUT": ["bicycle_group", "admin_group", "user_group"],
        "PATCH": ["bicycle_group", "admin_group", "user_group"],
        "DELETE": ["bicycle_group", "admin_group", "user_group"],
    }


class BikeTrailerModelListView(generics.ListCreateAPIView):
    queryset = BikeTrailerModel.objects.all()
    serializer_class = BikeTrailerModelSerializer


class BikeTrailerModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeTrailerModel.objects.all()
    serializer_class = BikeTrailerModelSerializer


class BikeTrailerListView(generics.ListCreateAPIView):
    queryset = BikeTrailer.objects.all()
    serializer_class = BikeTrailerSerializer


class BikeTrailerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BikeTrailer.objects.all()
    serializer_class = BikeTrailerSerializer
