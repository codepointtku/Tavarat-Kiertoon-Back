"""tavarat_kiertoon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from bulletins.views import (
    BulletinDetailView,
    BulletinListView,
    BulletinSubjectDetailView,
    BulletinSubjectListView,
)
from categories import views
from contact_forms.views import ContactFormDetailView, ContactFormListView
from orders.views import (
    OrderDetailView,
    OrderListView,
    ShoppingCartDetailView,
    ShoppingCartListView,
)
from products.views import (
    CategoryProductListView,
    ColorDetailView,
    ColorListView,
    PictureDetailView,
    PictureListView,
    ProductDetailView,
    ProductListView,
    StorageDetailView,
    StorageListView,
)
from users.views import (
    GroupListView,
    GroupNameView,
    UserCreateListView,
    UserDetailsListView,
    UserDetailsListView_limited,
    UserDetailsSingleView_limited,
    UserSingleGetView,
    UserView_login,
    UserView_password,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("storages/", StorageListView.as_view()),
    path("storages/<int:pk>/", StorageDetailView.as_view()),
    path("pictures/", PictureListView.as_view()),
    path("pictures/<int:pk>/", PictureDetailView.as_view()),
    path("colors/", ColorListView.as_view()),
    path("colors/<int:pk>/", ColorDetailView.as_view()),
    path("shopping_carts/", ShoppingCartListView.as_view()),
    path("shopping_carts/<int:pk>", ShoppingCartDetailView.as_view()),
    path("orders/", OrderListView.as_view()),
    path("orders/<int:pk>", OrderDetailView.as_view()),
    path("products/", ProductListView.as_view()),
    path("categories/<int:category_id>/products/", CategoryProductListView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),
    path("contact_forms/", ContactFormListView.as_view()),
    path("contact_forms/<int:pk>/", ContactFormDetailView.as_view()),
    path("categories/", views.categories),
    path("categories/<int:category_id>/", views.category),
    path("users/", UserDetailsListView.as_view()),
    path("users/create/", UserCreateListView.as_view()),
    path("users/<int:pk>/", UserSingleGetView.as_view()),
    path("users/limited/", UserDetailsListView_limited.as_view()),
    path("users/limited/<int:pk>", UserDetailsSingleView_limited.as_view()),
    path("users/password/<int:pk>/", UserView_password.as_view()),
    path("users/groups/", GroupListView.as_view()),
    path("users/groups/<int:pk>/", GroupNameView.as_view()),
    path("users/login/", UserView_login.as_view()),
    path("bulletins/", BulletinListView.as_view()),
    path("bulletins/<int:pk>", BulletinDetailView.as_view()),
    path("bulletin_subjects/", BulletinSubjectListView.as_view()),
    path("bulletin_subjects/<int:pk>", BulletinSubjectDetailView.as_view()),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # works only during developoment? check when ready for deplayment?
