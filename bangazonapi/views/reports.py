from django.shortcuts import render
from bangazonapi.models import Order


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
