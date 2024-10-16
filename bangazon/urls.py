from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from bangazonapi.models import *
from bangazonapi.views import *

# pylint: disable=invalid-name
router = routers.DefaultRouter(trailing_slash=False)
router.register(r"products", Products, "product")
router.register(r"categories", ProductCategories, "productcategory")
router.register(r"lineitems", LineItems, "orderproduct")
router.register(r"customers", Customers, "customer")
router.register(r"users", Users, "user")
router.register(r"orders", Orders, basename="order")
router.register(r"cart", Cart, "cart")
router.register(r"paymenttypes", Payments, "payment")
router.register(r"profile", Profile, "profile")
router.register(r"stores", StoreViewSet, "store")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("register", register_user),
    path("login", login_user),
    path("api-token-auth", obtain_auth_token),
    path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
    # Reports URLs
    path(
        "reports/",
        include(
            [
                path(
                    "incomplete_orders",
                    reports.incomplete_orders_report,
                    name="incomplete_orders",
                ),
                path(
                    "expensiveproducts",
                    reports.expensive_products_report,
                    name="expensive_products",
                ),
                path(
                    "completed_orders",
                    reports.completed_orders_report,
                    name="completed_orders",
                ),
                path(
                    "inexpensive_products",
                    reports.inexpensive_products_report,
                    name="inexpensive_products",
                ),
                path(
                    "favoritesellers",
                    reports.favorite_sellers_report,
                    name="favoritesellers",
                ),
                # Add more report URLs here as needed
            ]
        ),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
