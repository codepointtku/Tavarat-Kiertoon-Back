"""The bike rental views."""

import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response

from bikes.models import Bike, BikePackage
from bikes.serializers import BikePackageSerializer, BikeSerializer


@api_view(["GET"])
def test(request):
    """Just a test function I'll remove later."""

    today = datetime.date.today()
    available_from = today + datetime.timedelta(days=7)
    available_to = today + datetime.timedelta(days=183)

    bike_serializer = BikeSerializer(Bike.objects.all(), many=True)
    bike_package_serializer = BikePackageSerializer(
        BikePackage.objects.all(), many=True
    )

    for index, bike in enumerate(bike_serializer.data):
        taken = {}
        for bike in bike["stock"]:
            for rental in bike["rental"]:
                start_date = datetime.datetime.fromisoformat(rental["start_date"])
                end_date = datetime.datetime.fromisoformat(rental["end_date"])
                date = start_date
                while date <= end_date:
                    date_str = date.strftime("%d.%m.%Y")
                    if date_str in taken:
                        taken[date_str] = 1 + taken[date_str]
                    else:
                        taken[date_str] = 1
                    date += datetime.timedelta(days=1)
        bike_serializer.data[index]["taken"] = taken
        del bike_serializer.data[index]["stock"]

    for index, package in enumerate(bike_package_serializer.data):
        serializer_package = bike_package_serializer.data[index]
        # serializer_package["type"] = "Paketti"
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
            # "db_bikes": bike_serializer.data,
            "packages": bike_package_serializer.data,
            # "bikes": [
            #     {
            #         "id": 1,
            #         "name": "Punainen hieno pyörä",
            #         "description": "Hyväkuntone hieno pyörä punainen suoraa 80-luvulta",
            #         "max_available": 0,
            #         "taken": {},
            #         "size": "14″",
            #         "type": "City",
            #         "color": "Punainen",
            #         "brand": "Hieno",
            #     },
            #     {
            #         "id": 2,
            #         "name": "Vihreä hyvä pyörä",
            #         "description": "Todella hyvä pyörä",
            #         "max_available": 17,
            #         "taken": {"15.03.2023": 1, "16.03.2023": 2, "20.03.2023": 1},
            #         "size": "21″",
            #         "type": "BMX",
            #         "color": "Vihreä",
            #         "brand": "Hyvä",
            #     },
            #     {
            #         "id": 3,
            #         "name": "Toinen hyvä pyörä",
            #         "description": "Todella hyvä pyörä myös",
            #         "max_available": 9,
            #         "taken": {"15.03.2023": 1, "16.03.2023": 2, "20.03.2023": 1},
            #         "size": "16″",
            #         "type": "City",
            #         "color": "Vihreä",
            #         "brand": "Hyvä",
            #     },
            #     {
            #         "id": 4,
            #         "name": "Päiväkoti -paketti",
            #         "description": "16″ pyöriä 7 kpl, 14″ pyöriä 3 kpl, potkupyöriä 10 kpl, pyöräilykypäriä 20 kpl, käsipumppu, jalkapumppu, monitoimityökalu",
            #         "max_available": 2,
            #         "taken": {"15.03.2023": 1, "16.03.2023": 2, "20.03.2023": 1},
            #         "size": "14″ & 16″",
            #         "type": "Paketti",
            #         "color": "Monia",
            #         "brand": "Hyvä",
            #     },
            #     {
            #         "id": 5,
            #         "name": "Koulu -paketti",
            #         "description": "20″ pyöriä 6 kpl, 24″ pyöriä 6 kpl, pyöräilykypäriä 13 kpl, käsipumppu, jalkapumppu, monitoimityökalu, molempia pyöriä olemassa 7 kpl, mutta tällä määrällä peräkärry on helppo lastata",
            #         "max_available": 2,
            #         "taken": {"15.03.2023": 1, "16.03.2023": 2, "20.03.2023": 1},
            #         "size": "20″ & 24″",
            #         "type": "Paketti",
            #         "color": "Monia",
            #         "brand": "Hyvä",
            #     },
            # ],
        }
    )
