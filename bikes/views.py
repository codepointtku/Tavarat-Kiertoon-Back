import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response

# TODO: Write docstrings


@api_view(["GET"])
def test(request):
    today = datetime.date.today()
    available_from = today + datetime.timedelta(days=7)
    available_to = today + datetime.timedelta(days=183)
    monday = today - datetime.timedelta(days=today.weekday() + 7)
    return Response(
        {
            "date_info": {
                "today": today,
                "available_from": available_from,
                "available_to": available_to,
                "monday": monday,
            },
            "bikes": {},
        }
    )
