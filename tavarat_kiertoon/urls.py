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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from bulletins.views import BulletinDetailView, BulletinListView
from categories.views import CategoryDetailView, CategoryListView, CategoryTreeView
from contact_forms.views import (
    ContactDetailView,
    ContactFormDetailView,
    ContactFormListView,
    ContactListView,
)
from orders.views import (
    OrderDetailView,
    OrderEmailRecipientDetailView,
    OrderEmailRecipientListView,
    OrderListView,
    OrderSelfListView,
    ShoppingCartDetailView,
    ShoppingCartListView,
)
from products.views import (
    ColorDetailView,
    ColorListView,
    PictureDetailView,
    PictureListView,
    ProductDetailView,
    ProductItemDetailView,
    ProductItemListView,
    ProductListView,
    ProductStorageTransferView,
    ShoppingCartAvailableAmountList,
    StorageDetailView,
    StorageListView,
)
from users.views import (
    GroupListView,
    GroupPermissionUpdateView,
    UserActivationView,
    UserAddressAdminCreateView,
    UserAddressAdminEditView,
    UserAddressEditDeleteView,
    UserAddressEditView,
    UserCreateListView,
    UserDetailsListView,
    UserEmailChangeFinishView,
    UserEmailChangeView,
    UserLoginView,
    UserLogoutView,
    UserLogView,
    UserPasswordResetMailValidationView,
    UserPasswordResetMailView,
    UserSearchWatcheAdminView,
    UserSearchWatchesAdminView,
    UserSearchWatchesUserView,
    UserSearchWatcheUserView,
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
    path("shopping_cart/available_amount/", ShoppingCartAvailableAmountList.as_view()),
    path("orders/", OrderListView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),
    path("orders/emailrecipients/", OrderEmailRecipientListView.as_view()),
    path("orders/emailrecipients/<int:pk>/", OrderEmailRecipientDetailView.as_view()),
    path("orders/user/", OrderSelfListView.as_view()),
    path("products/", ProductListView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),
    path("products/items/", ProductItemListView.as_view()),
    path("products/items/<int:pk>", ProductItemDetailView.as_view()),
    path("products/transfer/", ProductStorageTransferView.as_view()),
    path("contact_forms/", ContactFormListView.as_view()),
    path("contact_forms/<int:pk>/", ContactFormDetailView.as_view()),
    path("categories/", CategoryListView.as_view()),
    path("categories/<int:pk>/", CategoryDetailView.as_view()),
    path("categories/tree/", CategoryTreeView.as_view()),
    path("bulletins/", BulletinListView.as_view()),
    path("bulletins/<int:pk>", BulletinDetailView.as_view()),
    path("bikes/", include("bikes.urls")),
    path("contacts/", ContactListView.as_view()),
    path("contacts/<int:pk>", ContactDetailView.as_view()),
    path("api-auth/", include("rest_framework.urls")),
    path("users/", UserDetailsListView.as_view()),
    path("user/", UserUpdateInfoView.as_view()),
    path("user/address/edit/", UserAddressEditView.as_view()),
    path("user/address/edit/<int:pk>/", UserAddressEditDeleteView.as_view()),
    path("user/searchwatch/", UserSearchWatchesUserView.as_view()),
    path("user/searchwatch/<int:pk>/", UserSearchWatcheUserView.as_view()),
    path("users/create/", UserCreateListView.as_view()),
    path("users/<int:pk>/", UserUpdateSingleView.as_view()),
    path("users/<int:pk>/groups/permission/", GroupPermissionUpdateView.as_view()),
    path("users/address/", UserAddressAdminCreateView.as_view()),
    path("users/address/<int:pk>/", UserAddressAdminEditView.as_view()),
    path("users/searchwatch/", UserSearchWatchesAdminView.as_view()),
    path(
        "users/searchwatch/<int:pk>/",
        UserSearchWatcheAdminView.as_view(),
    ),
    path("users/groups/", GroupListView.as_view()),
    path("users/login/", UserLoginView.as_view(), name="token_obtain_pair_http"),
    path("users/login/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("users/logout/", UserLogoutView.as_view()),
    path("users/activate/", UserActivationView.as_view()),
    path("users/password/resetemail/", UserPasswordResetMailView.as_view()),
    path(
        "users/password/reset/",
        UserPasswordResetMailValidationView.as_view(),
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swag",
    ),
    path("users/emailchange/", UserEmailChangeView.as_view()),
    path("users/emailchange/finish/", UserEmailChangeFinishView.as_view()),
    path("users/log/", UserLogView.as_view()),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # works only during developoment? check when ready for deplayment?
