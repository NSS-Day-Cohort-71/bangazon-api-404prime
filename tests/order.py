import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone


class OrderTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a product category
        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        # Create a product
        url = "/products"
        data = {
            "name": "Kite",
            "price": 14.99,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_order(self):
        """
        Ensure we can add a product to an order.
        """
        # Add product to order
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

    def test_remove_product_from_order(self):
        """
        Ensure we can remove a product from an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Remove product from cart
        url = "/cart/1"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)

    # TODO: Complete order by adding payment type & completed_date

    def test_complete_order(self):
        """
        Ensure we can complete an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Get the order ID
        url = "/orders"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)
        order_id = json_response[0]["id"]

        # Add payment type
        url = "/paymenttypes"
        data = {
            "merchant_name": "Visa",
            "account_number": "987654321",
            "expiration_date": "2022-12-31",
            "create_date": "2020-12-31",
            "customer_id": 1,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Complete order
        url = f"/orders/{order_id}/complete"
        completed_date = timezone.now().isoformat()
        data = {"payment_type": 1, "completed_date": completed_date}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get order and verify it was completed
        url = "/orders/1"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(json_response["completed_date"])
        self.assertIsNotNone(json_response["payment_type"])

    # TODO: New line item is not added to closed order

def test_prevent_add_to_closed_order(self):
    """
    Ensure we cannot add a product to a closed order.
    """
    # Add product
    self.test_add_product_to_order()

    # Get the order ID
    url = "/orders"
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.get(url, None, format="json")
    json_response = json.loads(response.content)
    order_id = json_response[0]["id"]

    # Get the initial line items for the order
    url = f"/orders/{order_id}/lineitems"
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.get(url, None, format="json")
    initial_line_items = json.loads(response.content)

    # Complete order
    url = f"/orders/{order_id}/complete"
    completed_date = timezone.now().isoformat()
    data = {"payment_type": 1, "completed_date": completed_date}
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.put(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Attempt to add new line item to the closed order
    url = f"/orders/{order_id}/lineitems"
    data = {"product_id": 2}  # Replace with the ID of the product you want to add
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Verify that the request fails

    # Verify that the order's line items have not changed
    url = f"/orders/{order_id}/lineitems"
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.get(url, None, format="json")
    updated_line_items = json.loads(response.content)

    self.assertEqual(initial_line_items, updated_line_items)  # Verify that the line items are the same

    # Verify that the order is still closed
    url = f"/orders/{order_id}"
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
    response = self.client.get(url, None, format="json")
    json_response = json.loads(response.content)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(json_response["status"], "closed")