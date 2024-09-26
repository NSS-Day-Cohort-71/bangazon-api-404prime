from django.db import models
from .customer import Customer  # Assuming Customer is the seller


class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="stores"
    )

    @property
    def items_for_sale(self):
        """Returns the number of items currently for sale in the store"""
        return self.products.count()

    def __str__(self):
        return self.name
