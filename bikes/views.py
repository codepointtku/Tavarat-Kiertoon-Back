import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response

# TODO: Write docstrings


@api_view(["GET"])
def test(request):
    """Just a test function I'll remove later."""

    today = datetime.date.today()
    available_from = today + datetime.timedelta(days=7)
    available_to = today + datetime.timedelta(days=183)

    return Response(
        {
            "date_info": {
                "available_from": available_from,
                "available_to": available_to,
            },
            "bikes": [
                {
                    "id": 1,
                    "name": "Punainen hieno pyörä",
                    "description": "Hyväkuntone hieno pyörä punainen suoraa 80-luvulta",
                    "available": 0,
                    "max_available": 0,
                    "taken": {},
                    "size": "14″",
                    "type": "City",
                    "color": "Punainen",
                    "brand": "Hieno",
                },
                {
                    "id": 2,
                    "name": "Vihreä hyvä pyörä",
                    "description": "Todella hyvä pyörä",
                    "available": 5,
                    "max_available": 17,
                    "taken": {"15.3.2023": 1, "16.3.2023": 2, "20.3.2023": 1},
                    "size": "21″",
                    "type": "BMX",
                    "color": "Vihreä",
                    "brand": "Hyvä",
                },
                {
                    "id": 3,
                    "name": "Toinen hyvä pyörä",
                    "description": "Todella hyvä pyörä myös",
                    "available": 2,
                    "max_available": 9,
                    "taken": {"15.3.2023": 1, "16.3.2023": 2, "20.3.2023": 1},
                    "size": "16″",
                    "type": "City",
                    "color": "Vihreä",
                    "brand": "Hyvä",
                },
                {
                    "id": 4,
                    "name": "Päiväkoti -paketti",
                    "description": "16″ pyöriä 7 kpl, 14″ pyöriä 3 kpl, potkupyöriä 10 kpl, pyöräilykypäriä 20 kpl, käsipumppu, jalkapumppu, monitoimityökalu",
                    "available": 1,
                    "max_available": 2,
                    "taken": {"15.3.2023": 1, "16.3.2023": 2, "20.3.2023": 1},
                    "size": "14″ & 16″",
                    "type": "Paketti",
                    "color": "Monia",
                    "brand": "Hyvä",
                },
                {
                    "id": 5,
                    "name": "Koulu -paketti",
                    "description": "20″ pyöriä 6 kpl, 24″ pyöriä 6 kpl, pyöräilykypäriä 13 kpl, käsipumppu, jalkapumppu, monitoimityökalu, molempia pyöriä olemassa 7 kpl, mutta tällä määrällä peräkärry on helppo lastata",
                    "available": 1,
                    "max_available": 2,
                    "taken": {"15.3.2023": 1, "16.3.2023": 2, "20.3.2023": 1},
                    "size": "20″ & 24″",
                    "type": "Paketti",
                    "color": "Monia",
                    "brand": "Hyvä",
                },
            ],
        }
    )
