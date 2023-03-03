"""Url paths of the bike rental app."""
from django.urls import path

from . import views

app_name = "bikes"
urlpatterns = [
    path("", views.test, name="test"),
    path("stock", views.BikeStockList.as_view(), name="bike_stock"),
]
