"""View module for handling requests about customer profiles"""

import datetime
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import (
    Order,
    Customer,
    Product,
    OrderProduct,
    Favorite,
    Store,
    Recommendation,
)
from .product import ProductSerializer
from .order import OrderSerializer
from .store import StoreSerializer


class Profile(ViewSet):
    """Request handlers for user profile info in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        @api {GET} /profile GET user profile info
        @apiName GetProfile
        @apiGroup UserProfile

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {Number} id Profile id
        @apiSuccess (200) {String} url URI of customer profile
        @apiSuccess (200) {Object} user Related user object
        @apiSuccess (200) {String} user.first_name Customer first name
        @apiSuccess (200) {String} user.last_name Customer last name
        @apiSuccess (200) {String} user.email Customer email
        @apiSuccess (200) {String} phone_number Customer phone number
        @apiSuccess (200) {String} address Customer address
        @apiSuccess (200) {Object[]} payment_types Array of user's payment types
        @apiSuccess (200) {Object[]} recommends Array of recommendations made by the user

        @apiSuccessExample {json} Success
            HTTP/1.1 200 OK
            {
                "id": 7,
                "url": "http://localhost:8000/customers/7",
                "user": {
                    "first_name": "Brenda",
                    "last_name": "Long",
                    "email": "brenda@brendalong.com"
                },
                "phone_number": "555-1212",
                "address": "100 Indefatiguable Way",
                "payment_types": [
                    {
                        "url": "http://localhost:8000/paymenttypes/3",
                        "deleted": null,
                        "merchant_name": "Visa",
                        "account_number": "fj0398fjw0g89434",
                        "expiration_date": "2020-03-01",
                        "create_date": "2019-03-11",
                        "customer": "http://localhost:8000/customers/7"
                    }
                ],
                "recommends": [
                    {
                        "product": {
                            "id": 32,
                            "name": "DB9"
                        },
                        "customer": {
                            "id": 5,
                            "user": {
                                "first_name": "Joe",
                                "last_name": "Shepherd",
                                "email": "joe@joeshepherd.com"
                            }
                        }
                    }
                ]
            }
        """
        try:
            # Get the authenticated user
            user = request.auth.user
            if not user:
                return Response(
                    {"message": "User profile not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get the customer associated with the user
            current_user = Customer.objects.get(user=request.auth.user)
            # Get recommendations made by this user
            current_user.recommends = Recommendation.objects.filter(
                recommender=current_user
            )

            serializer = ProfileSerializer(
                current_user,
                many=False,
                context={"request": request},
            )
            return Response(serializer.data)

        except Customer.DoesNotExist:
            return Response(
                {
                    "message": f"Customer profile not found for user {user.username} (id: {user.id}).",
                    "error": "CustomerDoesNotExist",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return Response(
                {"message": str(ex), "error": type(ex).__name__},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["get", "post", "delete"], detail=False)
    def cart(self, request):
        """Shopping cart manipulation"""

        current_user = Customer.objects.get(user=request.auth.user)

        if request.method == "DELETE":
            """
            @api {DELETE} /profile/cart DELETE all line items in cart
            @apiName DeleteCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccessExample {json} Success
                HTTP/1.1 204 No Content
            @apiError (404) {String} message  Not found message.
            """
            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                line_items = OrderProduct.objects.filter(order=open_order)
                line_items.delete()
                open_order.delete()
            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        if request.method == "GET":
            """
            @api {GET} /profile/cart GET line items in cart
            @apiName GetCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {Number} id Order cart
            @apiSuccess (200) {String} url URL of order
            @apiSuccess (200) {String} created_date Date created
            @apiSuccess (200) {Object} payment_type Payment Id used to complete order
            @apiSuccess (200) {String} customer URI for customer
            @apiSuccess (200) {Number} size Number of items in cart
            @apiSuccess (200) {Object[]} line_items Line items in cart
            @apiSuccess (200) {Number} line_items.id Line item id
            @apiSuccess (200) {Object} line_items.product Product in cart
            @apiSuccessExample {json} Success
                {
                    "id": 2,
                    "url": "http://localhost:8000/orders/2",
                    "created_date": "2019-04-12",
                    "payment_type": null,
                    "customer": "http://localhost:8000/customers/7",
                    "line_items": [
                        {
                            "id": 4,
                            "product": {
                                "id": 52,
                                "url": "http://localhost:8000/products/52",
                                "name": "900",
                                "price": 1296.98,
                                "number_sold": 0,
                                "description": "1987 Saab",
                                "quantity": 2,
                                "created_date": "2019-03-19",
                                "location": "Vratsa",
                                "image_path": null,
                                "average_rating": 0,
                                "category": {
                                    "url": "http://localhost:8000/productcategories/2",
                                    "name": "Auto"
                                }
                            }
                        }
                    ],
                    "size": 1
                }
            @apiError (404) {String} message  Not found message
            """
            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                line_items = OrderProduct.objects.filter(order=open_order)
                line_items = LineItemSerializer(
                    line_items, many=True, context={"request": request}
                )

                cart = {}
                cart["order"] = OrderSerializer(
                    open_order, many=False, context={"request": request}
                ).data
                cart["order"]["line_items"] = line_items.data
                cart["order"]["size"] = len(line_items.data)

            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(cart["order"])

        if request.method == "POST":
            """
            @api {POST} /profile/cart POST new product to cart
            @apiName AddToCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {Object} line_item Line items in cart
            @apiSuccess (200) {Number} line_item.id Line item id
            @apiSuccess (200) {Object} line_item.product Product in cart
            @apiSuccess (200) {Object} line_item.order Open order for cart
            @apiSuccessExample {json} Success
                {
                    "id": 14,
                    "product": {
                        "url": "http://localhost:8000/products/52",
                        "deleted": null,
                        "name": "900",
                        "price": 1296.98,
                        "description": "1987 Saab",
                        "quantity": 2,
                        "created_date": "2019-03-19",
                        "location": "Vratsa",
                        "image_path": null,
                        "customer": "http://localhost:8000/customers/7",
                        "category": "http://localhost:8000/productcategories/2"
                    },
                    "order": {
                        "url": "http://localhost:8000/orders/2",
                        "created_date": "2019-04-12",
                        "customer": "http://localhost:8000/customers/7",
                        "payment_type": null
                    }
                }

            @apiError (404) {String} message  Not found message
            """

            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)

            except Order.DoesNotExist as ex:
                open_order = Order()
                open_order.created_date = datetime.datetime.now()
                open_order.customer = current_user
                open_order.save()

            line_item = OrderProduct()
            line_item.product = Product.objects.get(pk=request.data["product_id"])
            line_item.product = Product.objects.get(pk=request.data["product_id"])
            line_item.order = open_order
            line_item.save()

            line_item_json = LineItemSerializer(
                line_item, many=False, context={"request": request}
            )

            return Response(line_item_json.data)

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=["get", "post", "delete"], detail=False)
    def favoritesellers(self, request):

        if request.method == "GET":
            """
            @api {GET} /profile/favoritesellers GET favorite sellers
            @apiName GetFavoriteSellers
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {id} id Favorite id
            @apiSuccess (200) {Object} seller Favorited seller
            @apiSuccess (200) {String} seller.url Seller URI
            @apiSuccess (200) {String} seller.phone_number Seller phone number
            @apiSuccess (200) {String} seller.address Seller address
            @apiSuccess (200) {String} seller.user Seller user profile URI
            @apiSuccessExample {json} Success
                [
                    {
                        "id": 1,
                        "seller": {
                            "url": "http://localhost:8000/customers/5",
                            "phone_number": "555-1212",
                            "address": "100 Endless Way",
                            "user": "http://localhost:8000/users/6"
                        }
                    },
                    {
                        "id": 2,
                        "seller": {
                            "url": "http://localhost:8000/customers/6",
                            "phone_number": "555-1212",
                            "address": "100 Dauntless Way",
                            "user": "http://localhost:8000/users/7"
                        }
                    },
                    {
                        "id": 3,
                        "seller": {
                            "url": "http://localhost:8000/customers/7",
                            "phone_number": "555-1212",
                            "address": "100 Indefatiguable Way",
                            "user": "http://localhost:8000/users/8"
                        }
                    }
                ]
            """
            customer = Customer.objects.get(user=request.auth.user)
            favorites = (
                Favorite.objects.filter(customer=customer)
                .select_related("seller__user")
                .prefetch_related("seller__stores")
            )

            serializer = FavoriteSerializer(
                favorites, many=True, context={"request": request}
            )
            return Response(serializer.data)

        elif request.method == "POST":
            """
            @api {POST} /profile/favoritesellers POST new favorite seller
            @apiName AddFavoriteSeller
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiParam {Number} store_id ID of the store to favorite

            @apiSuccess (201) {Object} favorite Newly created favorite
            @apiSuccess (201) {Number} favorite.id Favorite id
            @apiSuccess (201) {Object} favorite.seller Favorited seller details
            @apiSuccessExample {json} Success
                {
                    "id": 4,
                    "seller": {
                        "url": "http://localhost:8000/customers/8",
                        "phone_number": "555-1212",
                        "address": "100 New Favorite Way",
                        "user": "http://localhost:8000/users/9"
                    }
                }

            @apiError (404) {Object} error Error message if store not found
            @apiError (400) {Object} error Error message if store_id is missing
            """
            customer = Customer.objects.get(user=request.auth.user)
            store_id = request.data.get("store_id")

            if not store_id:
                return Response(
                    {"error": "store_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                store = Store.objects.get(id=store_id)
                seller = store.seller
            except Store.DoesNotExist:
                return Response(
                    {"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND
                )

            if seller == customer:
                return Response(
                    {"error": "You cannot favorite your own store"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            favorite, created = Favorite.objects.get_or_create(
                customer=customer, seller=seller
            )

            serializer = FavoriteSerializer(favorite, context={"request": request})
            if created:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            """
            @api {DELETE} /profile/favoritesellers DELETE favorite seller
            @apiName RemoveFavoriteSeller
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiParam {Number} favorite_id ID of the favorite to remove

            @apiSuccess (204) {Object} null No content, successful deletion

            @apiError (404) {Object} error Error message if favorite not found
            @apiError (400) {Object} error Error message if favorite_id is missing
            @apiError (403) {Object} error Error message if user doesn't have permission
            """
            favorite_id = request.data.get("favorite_id")

            if not favorite_id:
                return Response(
                    {"error": "favorite_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                favorite = Favorite.objects.get(pk=favorite_id)

                # Check if the authenticated user owns this favorite
                if favorite.customer.user != request.auth.user:
                    return Response(
                        {"error": "You do not have permission to delete this favorite"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Favorite.DoesNotExist:
                return Response(
                    {"error": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for products

    Arguments:
        serializers
    """

    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        fields = ("id", "product")
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for customer profile

    Arguments:
        serializers
    """

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
        depth = 1


class CustomerSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendation customers"""

    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
        )


class ProfileProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    class Meta:
        model = Product
        fields = ("id", "name", "price")


class RecommenderSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendations"""

    customer = CustomerSerializer()
    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = (
            "product",
            "customer",
        )


class RecommendationSerializer(serializers.ModelSerializer):

    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = ("product",)


class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer for customer profile

    Arguments:
        serializers
    """

    user = UserSerializer(many=False)
    recommends = RecommenderSerializer(many=True)
    stores = StoreSerializer(many=True, read_only=True)
    recommendations_received = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "url",
            "user",
            "phone_number",
            "address",
            "payment_types",
            "recommends",
            "stores",
            "recommendations_received",
        )
        depth = 1

    def get_recommendations_received(self, obj):
        recommendations = Recommendation.objects.filter(customer=obj)
        return RecommendationSerializer(
            recommendations, many=True, context=self.context
        ).data


class FavoriteUserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for favorite sellers user

    Arguments:
        serializers
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
        depth = 1


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ("id", "name", "description")


class FavoriteSellerSerializer(serializers.HyperlinkedModelSerializer):
    user = FavoriteUserSerializer(many=False)
    store = StoreSerializer(source="stores.first", read_only=True)

    class Meta:
        model = Customer
        fields = ("id", "url", "user", "phone_number", "address", "store")
        depth = 1


class FavoriteSerializer(serializers.HyperlinkedModelSerializer):
    seller = FavoriteSellerSerializer(many=False)

    class Meta:
        model = Favorite
        fields = ("id", "seller")
        depth = 2
