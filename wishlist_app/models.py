
from django.db import models
from django.contrib.auth.models import User
from product_app.models import Product


class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_product_in_wishlist'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"