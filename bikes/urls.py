"""Url paths of the bike rental app."""
from django.urls import path

from . import views

app_name = "bikes"
urlpatterns = [
    path("", views.MainBikeList.as_view()),
    path("stock", views.BikeStockList.as_view()),
    path("stock/<int:pk>/", views.BikeStockDetailView.as_view()),
    path("rental/", views.RentalListView.as_view()),
    path("rental/<int:pk>/", views.RentalDetailView.as_view())
]
