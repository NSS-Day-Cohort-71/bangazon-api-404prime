from django.db import models
from django.contrib.auth.models import User
from .product import Product


class FavoriteProduct(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='products'
    )

    class Meta:
        unique_together = ('user', 'product')
