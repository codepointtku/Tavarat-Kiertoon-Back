"""The bike rental views."""

import datetime

from rest_framework import generics

# from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from bikes.models import Bike, BikePackage, BikeStock
from bikes.serializers import BikePackageSerializer, BikeSerializer, BikeStockSerializer


class BikeStockList(generics.ListAPIView):
    queryset = BikeStock.objects.all()
    serializer_class = BikeStockSerializer
    # permission_classes = [isAdminUser]


class MainBikeList(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        today = datetime.date.today()
        available_from = today + datetime.timedelta(days=7)
        available_to = today + datetime.timedelta(days=183)

        bike_serializer = BikeSerializer(Bike.objects.all(), many=True)
        bike_package_serializer = BikePackageSerializer(
            BikePackage.objects.all(), many=True
        )

        for index, bike in enumerate(bike_serializer.data):
            unavailable = {}
            for bike in bike["stock"]:
                for rental in bike["rental"]:
                    start_date = datetime.datetime.fromisoformat(rental["start_date"])
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
            del bike_serializer.data[index]["stock"]

        for index, package in enumerate(bike_package_serializer.data):
            serializer_package = bike_package_serializer.data[index]
            serializer_package["type"] = "Paketti"
            serializer_package["unavailable"] = {}
            serializer_package["max_available"] = 1
            serializer_package["brand"] = None
            serializer_package["color"] = None
            for bike in package["bikes"]:
                bike_object = Bike.objects.get(id=bike["bike"])
                if "size" in serializer_package:
                    serializer_package[
                        "size"
                    ] = f"{serializer_package['size']} & {bike_object.size.name}"
                else:
                    serializer_package["size"] = bike_object.size.name

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
