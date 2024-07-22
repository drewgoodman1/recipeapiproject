from django.db import models
from .recipe import Recipe
from .ingredient import Ingredient


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )

    def __str__(self):
        return f"{self.recipe.description} - {self.ingredient.name}"
