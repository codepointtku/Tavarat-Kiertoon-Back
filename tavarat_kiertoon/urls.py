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
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from bulletins.views import (
    BulletinDetailView,
    BulletinListView,
    BulletinSubjectDetailView,
    BulletinSubjectListView,
)
from categories.views import CategoryDetailView, CategoryListView
from contact_forms.views import (
    ContactDetailView,
    ContactFormDetailView,
    ContactFormListView,
    ContactListView,
)
from orders.views import (
    OrderDetailView,
    OrderListView,
    OrderSelfListView,
    ShoppingCartDetailView,
    ShoppingCartListView,
)
from products.views import (
    CategoryTreeView,
    ColorDetailView,
    ColorListView,
    PictureDetailView,
    PictureListView,
    ProductDetailView,
    ProductListView,
    ProductStorageTransferView,
    StorageDetailView,
    StorageListView,
)
from users.views import (
    GroupListView,
    GroupNameView,
    GroupPermissionCheckView,
    GroupPermissionUpdateView,
    UserAddressAddView,
    UserAddressEditView,
    UserAddressListView,
    UserCreateListView,
    UserDetailLimitedView,
    UserDetailsListLimitedView,
    UserDetailsListView,
    UserLoggedInDetailView,
    UserLoginTestView,
    UserLoginView,
    UserLogoutView,
    UserSingleGetView,
    UserTokenRefreshView,
    UserUpdateInfoView,
    UserUpdateSingleView,
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
    path("shopping_cart/", ShoppingCartDetailView.as_view()),
    path("orders/", OrderListView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),
    path("orders/user/", OrderSelfListView.as_view()),
    path("products/", ProductListView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),
    path("products/transfer/", ProductStorageTransferView.as_view()),
    path("contact_forms/", ContactFormListView.as_view()),
    path("contact_forms/<int:pk>/", ContactFormDetailView.as_view()),
    path("categories/", CategoryListView.as_view()),
    path("categories/<int:pk>/", CategoryDetailView.as_view()),
    path("categories/tree/", CategoryTreeView.as_view()),
    path("users/", UserDetailsListView.as_view()),
    path("user/", UserLoggedInDetailView.as_view()),
    path("users/create/", UserCreateListView.as_view()),
    path("users/<int:pk>/", UserSingleGetView.as_view()),
    path("users/address/", UserAddressListView.as_view()),
    path("users/address/add", UserAddressAddView.as_view()),
    path("users/address/<int:pk>", UserAddressEditView.as_view()),
    path("users/limited/", UserDetailsListLimitedView.as_view()),
    path("users/limited/<int:pk>", UserDetailLimitedView.as_view()),
    path("users/groups/", GroupListView.as_view()),
    path("users/groups/<int:pk>/", GroupNameView.as_view()),
    path("users/groups/permission/", GroupPermissionCheckView.as_view()),
    path("users/groups/permission/<int:pk>/", GroupPermissionUpdateView.as_view()),
    path("users/login_check/", UserLoginTestView.as_view()),
    path("users/logout/", UserLogoutView.as_view()),
    path("users/update/", UserUpdateInfoView.as_view()),
    path("users/update/<int:pk>/", UserUpdateSingleView.as_view()),
    path("bulletins/", BulletinListView.as_view()),
    path("bulletins/<int:pk>", BulletinDetailView.as_view()),
    path("bulletin_subjects/", BulletinSubjectListView.as_view()),
    path("bulletin_subjects/<int:pk>", BulletinSubjectDetailView.as_view()),
    path("bikes/", include("bikes.urls")),
    path("contacts/", ContactListView.as_view()),
    path("contacts/<int:pk>", ContactDetailView.as_view()),
    path("api-auth/", include("rest_framework.urls")),
    path("users/login/", UserLoginView.as_view(), name="token_obtain_pair_http"),
    path("users/login/test/", UserLoginTestView.as_view(), name="token_obtain_pair"),
    path("users/login/refresh/", UserTokenRefreshView.as_view(), name="token_refrest"),
    path("users/login/verify/", TokenVerifyView.as_view(), name="token_verify"),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # works only during developoment? check when ready for deplayment?
