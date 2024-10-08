from django.db import models
from django.contrib.auth.models import User
from .product import Product


class FavoriteProduct(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.DO_NOTHING,
    )
    product = models.ForeignKey(
        Product, on_delete=models.DO_NOTHING, related_name='products'
    )

    class Meta:
        unique_together = ('user', 'product')
