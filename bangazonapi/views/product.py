"""View module for handling requests about products"""

from rest_framework.decorators import action
from bangazonapi.models.recommendation import Recommendation
from bangazonapi.models import FavoriteProduct
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Product, Customer, ProductCategory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from .customer import CustomerSerializer
from .store import StoreSerializer
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    store = StoreSerializer()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "number_sold",
            "description",
            "quantity",
            "created_date",
            "location",
            "image_path",
            "average_rating",
            "can_be_rated",
            "store",
            "is_liked",
        )

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and hasattr(obj, "_request"):
            return obj.is_liked
        return False


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /products POST new product
        @apiName CreateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Short form name of product
        @apiParam {Number} price Cost of product
        @apiParam {String} description Long form description of product
        @apiParam {Number} quantity Number of items to sell
        @apiParam {String} location City where product is located
        @apiParam {Number} category_id Category of product
        @apiParamExample {json} Input
            {
                "name": "Kite",
                "price": 14.99,
                "description": "It flies high",
                "quantity": 60,
                "location": "Pittsburgh",
                "category_id": 4
            }

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        new_product.customer = customer

        # Assign the product category
        product_category = ProductCategory.objects.get(pk=request.data["categoryId"])
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{new_product.id}-{request.data["name"]}.{ext}',
            )

            new_product.image_path = data

        new_product.save()

        serializer = ProductSerializer(new_product, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /products/:id GET product
        @apiName GetProduct
        @apiGroup Product

        @apiParam {id} id Product Id

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product = Product.objects.get(pk=pk)
            product.set_request(request)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data)
        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /products/:id PUT changes to product
        @apiName UpdateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        # Assign the product category
        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            product = Product.objects.get(pk=pk)
            product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """
        @api {GET} /products GET all products
        @apiName ListProducts
        @apiGroup Product

        @apiParam {Number} store_id (Optional) Filter products by store ID
        @apiParam {Number} category_id (Optional) Filter products by category ID
        @apiParam {Number} min_price (Optional) Filter products by minimum price
        @apiParam {Number} max_price (Optional) Filter products by maximum price
        @apiParam {Number} quantity (Optional) Filter products by minimum quantity
        @apiParam {Number} number_sold (Optional) Filter products by minimum number sold

        @apiSuccess (200) {Object[]} products Array of products
        @apiSuccessExample {json} Success
            [
                {
                    "id": 101,
                    "name": "Kite",
                    "price": 14.99,
                    "number_sold": 0,
                    "description": "It flies high",
                    "quantity": 60,
                    "created_date": "2019-10-23",
                    "location": "Pittsburgh",
                    "image_path": null,
                    "average_rating": 0,
                    "category": {
                        "url": "http://localhost:8000/productcategories/6",
                        "name": "Games/Toys"
                    },
                    "store": {
                        "id": 1,
                        "name": "My Store"
                    }
                },
                # ... more products
            ]
        """
        products = Product.objects.all()

        # Filtering
        store_id = request.query_params.get("store_id", None)
        category_id = request.query_params.get("category_id", None)
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)
        quantity = request.query_params.get("quantity", None)
        number_sold = request.query_params.get("number_sold", None)
        location = request.query_params.get("location", None)
        direction = request.query_params.get("direction", None)
        sold_only = request.query_params.get("sold_only", "false").lower() == "true"

        if store_id:
            products = products.filter(store__id=store_id)

        if sold_only:
            products = products.annotate(
                orders_count=Count(
                    "lineitems",
                    filter=Q(lineitems__order__payment_type__isnull=False),
                )
            ).filter(orders_count__gt=0)

        if category_id:
            products = products.filter(category_id=category_id)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        if quantity:
            products = products.filter(quantity__gte=quantity)

        if number_sold:
            products = products.filter(number_sold__gte=number_sold)

        if location:
            products = products.filter(location__icontains=location)

        # Sorting based on direction
        if direction == "asc":
            products = products.order_by("price")
        elif direction == "desc":
            products = products.order_by("-price")

        for product in products:
            product.set_request(request)

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def recommend(self, request, pk=None):
        logger.info(f"Recommend method called with pk: {pk}")
        logger.info(f"Request data: {request.data}")

        product = get_object_or_404(Product, pk=pk)
        logger.info(f"Product found: {product}")

        recommender_id = request.data.get("recommender_id")
        recipient_id = request.data.get("recipient_id")
        logger.info(f"Recommender ID: {recommender_id}, Recipient ID: {recipient_id}")

        if not all([recommender_id, recipient_id]):
            return Response(
                {"error": "recommender_id and recipient_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check recommender
        try:
            recommender_user = User.objects.get(pk=recommender_id)
            logger.info(f"Recommender User found: {recommender_user}")
            recommender = Customer.objects.get(user=recommender_user)
            logger.info(f"Recommender Customer found: {recommender}")
        except User.DoesNotExist:
            logger.error(f"Recommender User with id {recommender_id} not found")
            return Response(
                {"error": f"Recommender User with id {recommender_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Customer.DoesNotExist:
            logger.error(f"Recommender Customer for User id {recommender_id} not found")
            return Response(
                {
                    "error": f"Recommender Customer for User id {recommender_id} not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check recipient
        try:
            recipient_user = User.objects.get(pk=recipient_id)
            logger.info(f"Recipient User found: {recipient_user}")
            recipient = Customer.objects.get(user=recipient_user)
            logger.info(f"Recipient Customer found: {recipient}")
        except User.DoesNotExist:
            logger.error(f"Recipient User with id {recipient_id} not found")
            return Response(
                {"error": f"Recipient User with id {recipient_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Customer.DoesNotExist:
            logger.error(f"Recipient Customer for User id {recipient_id} not found")
            return Response(
                {"error": f"Recipient Customer for User id {recipient_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recommendation = Recommendation.objects.create(
            product=product, customer=recipient, recommender=recommender
        )
        logger.info(f"Recommendation created: {recommendation}")

        return Response(
            {
                "id": recommendation.id,
                "product_id": product.id,
                "recipient_id": recipient.id,
                "recommender_id": recommender.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="like", url_name="like")
    def like_product(self, request, pk=None):
        try:
            # Fetch the product using pk (primary key)
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user has already liked this product
        favorite = FavoriteProduct.objects.filter(
            user=request.user, product=product
        ).first()

        if favorite:
            # If the product is already liked, provide an option to unlike
            return Response(
                {"status": "Product already liked", "favorite_id": favorite.id},
                status=status.HTTP_200_OK,
            )

        # Create a new favorite entry if not already liked
        favorite = FavoriteProduct.objects.create(user=request.user, product=product)

        return Response({}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="liked", url_name="liked")
    def list_favorites(self, request):
        user = request.user.id

        favorites = FavoriteProduct.objects.filter(user=user).select_related("product")

        favorite_products = [favorite.product for favorite in favorites]

        serializer = ProductSerializer(
            favorite_products, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="unlike", url_name="unlike")
    def delete_favorite(self, request, pk=None):
        try:
            # Get the favorite product based on the user's request
            favorite_to_delete = FavoriteProduct.objects.get(
                product__id=pk, user=request.user
            )
            favorite_to_delete.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except FavoriteProduct.DoesNotExist:
            return Response(
                {"error": "Favorite product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
