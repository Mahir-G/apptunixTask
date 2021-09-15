from django.db import models
from django.contrib.auth.models import User


class FoodItem(models.Model):
    name = models.CharField(max_length=128)
    cost = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CartItems(models.Model):
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Orders(models.Model):

    PRIORITIES = (
        (1, 'BAD'),
        (2, 'OK'),
        (3, 'MODERATE'),
        (4, 'GOOD'),
        (5, 'BEST')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivered = models.BooleanField(default=False)
    items = models.ManyToManyField(FoodItem)
    rating = models.IntegerField(default=None, null=True, choices=PRIORITIES)
