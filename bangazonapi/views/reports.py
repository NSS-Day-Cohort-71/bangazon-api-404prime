from django.shortcuts import render
from bangazonapi.models import Order, Product, Favorite
from django.db import connection


def incomplete_orders_report(request):
    # Check if 'status' query param is 'incomplete'
    status = request.GET.get("status", None)
    if status != "incomplete":
        # If the status is not incomplete, return an empty response or handle differently
        return render(request, "reports/incomplete_orders.html", {"orders_data": []})

    # Filter for incomplete (unpaid) orders: no payment type and no completed date
    orders = Order.objects.filter(
        payment_type__isnull=True, completed_date__isnull=True
    )

    # Prepare the data for the template
    orders_data = []
    for order in orders:
        # Calculate total cost of all items in the order
        total_cost = sum(item.product.price for item in order.lineitems.all())

        # Access the customer name via the related User model
        customer_name = order.customer.user.username

        # Append relevant data for the template
        orders_data.append(
            {
                "order_id": order.id,
                "customer_name": customer_name,
                "total_cost": total_cost,
            }
        )

    # Render the template with the data
    return render(
        request,
        "reports/orders/incomplete_orders.html",
        {"orders_data": orders_data},
    )


def completed_orders_report(request):
    status = request.GET.get("status", None)
    if status != "complete":
        return render(
            request, "reports/orders/completed_orders.html", {"orders_data": []}
        )

    orders = Order.objects.filter(
        payment_type__isnull=False, completed_date__isnull=False
    )

    orders_data = []
    for order in orders:
        total_cost = sum(item.product.price for item in order.lineitems.all())

        customer_name = order.customer.user.username

        orders_data.append(
            {
                "order_id": order.id,
                "customer_name": customer_name,
                "total_cost": total_cost,
                "payment_type": {
                    "merchant_name": order.payment_type.merchant_name,
                    "account_number": order.payment_type.account_number,
                    "expiration_date": order.payment_type.expiration_date,
                },
            }
        )
    return render(
        request,
        "reports/orders/completed_orders.html",
        {"orders_data": orders_data},
    )


def expensive_products_report(request):

    PRICE_THRESHOLD = 1000

    # "gte" = greater than or equal to
    expensive_products = Product.objects.filter(price__gte=PRICE_THRESHOLD)

    products_data = []
    for product in expensive_products:
        products_data.append(
            {"product_id": product.id, "name": product.name, "price": product.price}
        )

    return render(
        request,
        "reports/products/expensive_products.html",
        {"products_data": products_data},
    )


def inexpensive_products_report(request):
    # "lte" = less than or equal to
    inexpensive_products = Product.objects.filter(price__lte=999)

    products_data = []
    for product in inexpensive_products:
        products_data.append(
            {"product_id": product.id, "name": product.name, "price": product.price}
        )

    return render(
        request,
        "reports/products/inexpensive_products.html",
        {"products_data": products_data},
    )


def favorite_sellers_report(request):
    customer_id = request.GET.get("customer")

    if not customer_id:
        return render(request, "reports/favorite_sellers.html", {})

    try:
        customer_id = int(customer_id)
    except ValueError:
        return render(request, "reports/favorite_sellers.html", {})

    favorites = Favorite.objects.filter(customer_id=customer_id)

    if not favorites:
        return render(request, "reports/favorite_sellers.html", {})

    customer_name = favorites[0].customer.user.username
    favorite_sellers = [
        {
            "name": favorite.seller.user.username,
        }
        for favorite in favorites
    ]

    context = {
        "customer_name": customer_name,
        "favorite_sellers": favorite_sellers,
    }

    return render(request, "reports/favorite_sellers.html", context)
