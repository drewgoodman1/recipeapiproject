from django.db import models
from django.contrib.auth.models import User
from .ingredient import Ingredient


class Recipe(models.Model):
    description = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )

    def __str__(self):
        return self.description

    @property
    def pictures(self):
        return self.recipepicture_set.all()
