from django.db import models


class RecipePicture(models.Model):
    recipe = models.ForeignKey(
        "Recipe",  # Using string reference to avoid circular imports
        on_delete=models.CASCADE,
        related_name="pictures",
    )
    image = models.ImageField(upload_to="recipe_images/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image {self.id} for Recipe {self.recipe.description}"
