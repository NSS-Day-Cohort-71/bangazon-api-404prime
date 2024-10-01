import datetime
import json
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentTests(APITestCase):
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

    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        # Add product to order
        url = "/paymenttypes"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today(),
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "American Express")
        self.assertEqual(json_response["account_number"], "111-1111-1111")
        self.assertEqual(json_response["expiration_date"], "2024-12-31")
        self.assertEqual(json_response["create_date"], str(datetime.date.today()))

    def test_delete_payment_type(self):
        # Create a payment type
        url = "/paymenttypes"
        data = {
            "merchant_name": "Visa",
            "account_number": "222-2222-2222",
            "expiration_date": "2025-12-31",
            "create_date": datetime.date.today(),
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        # Store the id of the created payment type for later use
        payment_type_id = json_response["id"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "Visa")
        self.assertEqual(json_response["account_number"], "222-2222-2222")

        # Send DELETE request
        delete_url = f"{url}/{payment_type_id}"
        delete_response = self.client.delete(delete_url)

        # Check response status
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to retrieve the deleted payment type
        get_response = self.client.get(delete_url)

        # Assert that the payment type no longer exists
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
