from django.db import models
from .recipe import Recipe
from django.contrib.auth.models import User


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    def __str__(self):
        return f"Favorite: {self.user.username} -> {self.recipe.summary}"
