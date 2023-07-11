"""Url paths of the bike rental app."""
from django.urls import path

from . import views

app_name = "bikes"
urlpatterns = [
    path("", views.MainBikeList.as_view()),
    path("stock/", views.BikeStockListView.as_view()),
    path("stock/<int:pk>/", views.BikeStockDetailView.as_view()),
    path("rental/", views.RentalListView.as_view()),
    path("rental/<int:pk>/", views.RentalDetailView.as_view()),
    path("models/", views.BikeModelListView.as_view()),
    path("models/<int:pk>/", views.BikeModelDetailView.as_view()),
    path("packages/", views.BikePackageListView.as_view()),
    path("packages/<int:pk>/", views.BikePackageDetailView.as_view()),
    path("packageamounts/", views.BikeAmountListView.as_view()),
    path("type/", views.BikeTypeListView.as_view()),
    path("type/<int:pk>/", views.BikeTypeDetailView.as_view()),
    path("brand/", views.BikeBrandListView.as_view()),
    path("brand/<int:pk>/", views.BikeBrandDetailView.as_view()),
    path("size/", views.BikeSizeListView.as_view()),
    path("size/<int:pk>/", views.BikeSizeDetailView.as_view()),
    path("availabilitylist/", views.BikeAvailabilityList.as_view()),
]
