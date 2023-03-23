"""The bike rental views."""

import datetime
import math

# from rest_framework.permissions import IsAdminUser
from rest_framework import generics, status
from rest_framework.response import Response

from bikes.models import Bike, BikePackage, BikeStock, BikeRental
from bikes.serializers import BikePackageSerializer, BikeSerializer, BikeStockSerializer, BikeRentalSerializer


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


class RentalListView(generics.ListCreateAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer

    def post(self, request, *args, **kwargs):
        instance = request.data
        for i in request.data["bike_stock"]:
            print(request.data["bike_stock"])
            print(i)
        for i in request.data["bike_stock"]:
            itemset = Bike.objects.filter(i)
        available_itemset = itemset.exclude(id__in=instance.products.values("id"))
        removable_itemset = instance.products.filter(group_id=cartproduct.group_id)
        amount = request.data["amount"]

        for i in range(amount):
            instance.bike_stock.add(available_itemset[i])

        serializer = BikeRentalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RentalDetailView(generics.RetrieveAPIView):
    queryset = BikeRental.objects.all()
    serializer_class = BikeRentalSerializer