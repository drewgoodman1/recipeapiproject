import requests
import urllib.request
import uuid
import base64
from django.core.files.base import ContentFile
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from recipeapi.models.recipe import Recipe
from recipeapi.models.ingredient import Ingredient  # Import the Ingredient model
from recipeapi.models.recipe_picture import RecipePicture
from recipeapi.models.favorite_recipe import FavoriteRecipe
from .ingredient_view import IngredientSerializer
from rest_framework.decorators import action


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ("id", "user", "recipe")


class RecipePictureSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = RecipePicture
        fields = ["id", "image", "is_primary"]


class RecipeSerializer(serializers.ModelSerializer):
    favorites = FavoriteRecipeSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    pictures = RecipePictureSerializer(many=True)
    is_owner = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "description",
            "is_owner",
            "ingredients",
            "pictures",
            "favorites",
            "is_favorite",
        )
        depth = 1

    def get_is_owner(self, obj):
        request = self.context.get("request", None)
        if request is None or request.user.is_anonymous:
            return False
        return request.user == obj.user

    def get_is_favorite(self, obj):
        request = self.context.get("request", None)
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()


class RecipeView(viewsets.ViewSet):
    permission_classes = [
        IsAuthenticated
    ]  # Ensure the user is authenticated for all actions

    @action(detail=False, methods=["get"], url_path="my-recipes")
    def list_my_recipes(self, request):
        """List all recipes owned by the logged-in user or favorited by the logged-in user"""
        user = request.user
        owned_recipes = Recipe.objects.filter(user=user)
        favorited_recipes = Recipe.objects.filter(favorites__user=user)
        all_recipes = owned_recipes | favorited_recipes
        serialized = RecipeSerializer(
            all_recipes.distinct(), many=True, context={"request": request}
        )
        return Response(serialized.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="favorite")
    def favorite(self, request, pk=None):
        """Add or remove a recipe from user's favorites"""
        try:
            recipe = Recipe.objects.get(pk=pk)
            user = request.user
            favorite, created = FavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                favorite.delete()
                return Response(
                    {"message": "Removed from favorites"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            serialized = RecipeSerializer(recipe)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="favorites")
    def list_favorites(self, request):
        """List all favorite recipes for the logged-in user"""
        favorite_recipes = FavoriteRecipe.objects.filter(user=request.user)
        recipes = [favorite.recipe for favorite in favorite_recipes]
        serialized = RecipeSerializer(recipes, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
            if recipe.user != request.user:
                raise PermissionDenied(
                    "You do not have permission to view this recipe."
                )

            serialized = RecipeSerializer(recipe, context={"request": request})
            return Response(serialized.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        recipes = Recipe.objects.all()
        serialized = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
            if recipe.user != request.user:
                raise PermissionDenied(
                    "You do not have permission to delete this recipe."
                )
            recipe.delete()
            return Response(
                {"message": f"This recipe {pk} was removed"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        description = request.data.get("description", None)
        ingredients_data = request.data.get("ingredients", [])  # Correct variable name
        images = request.data.get("images", [])  # Updated to match client-side key

        if not description:
            return Response(
                {"error": "Description is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # these will be the pk's of our ingredients for the new recipe

        if isinstance(ingredients_data[0], int):
            new_recipe = Recipe.objects.create(
                user=request.user, description=description
            )
            new_recipe.ingredients.set(ingredients_data)
        else:
            # Ensure ingredients exist or create new ones
            ingredient_ids = []
            for ingredient_data in ingredients_data:
                name = ingredient_data.get("name", "").strip()
                if name:
                    ingredient, created = Ingredient.objects.get_or_create(name=name)
                    ingredient_ids.append(ingredient.id)
            # Create the new recipe once
            new_recipe = Recipe.objects.create(
                user=request.user, description=description
            )
            new_recipe.ingredients.set(ingredient_ids)

        # Handle image download and storage with requests
        for image_url in images:
            try:
                # Download the image from the URL
                response = requests.get(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                response.raise_for_status()  # Check if the request was successful
                image_content = response.content

                # Determine file extension
                ext = image_url.split(".")[
                    -1
                ].lower()  # Extract file extension from URL
                if ext not in ["jpg", "jpeg", "png", "gif"]:
                    ext = "jpg"  # Default to jpg if the extension is not recognized

                # Save the image to a ContentFile
                file_name = f"{new_recipe.id}-{uuid.uuid4()}.{ext}"
                data = ContentFile(image_content, name=file_name)

                # Save the image to the RecipePicture model
                RecipePicture.objects.create(recipe=new_recipe, image=data)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading or processing image: {e}")

            serialized_recipe = RecipeSerializer(
                new_recipe, context={"request": request}
            )
            return Response(serialized_recipe.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
            if recipe.user != request.user:
                raise PermissionDenied(
                    "You do not have permission to edit this recipe."
                )

            description = request.data.get("description", None)
            if description:
                recipe.description = description

            ingredient_ids = request.data.get("ingredients", None)
            if ingredient_ids is not None:
                recipe.ingredients.set(ingredient_ids)

            # Clear existing images
            RecipePicture.objects.filter(recipe=recipe).delete()

            # Handle new image upload
            images = request.data.get("images", [])
            if images:
                img = images[0]
                format, imgstr = img.split(";base64,")
                ext = format.split("/")[-1]
                file_name = f"{recipe.id}-{uuid.uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=file_name)
                RecipePicture.objects.create(recipe=recipe, image=data, is_primary=True)

            recipe.save()
            serialized_recipe = RecipeSerializer(recipe, context={"request": request})
            return Response(serialized_recipe.data, status=status.HTTP_200_OK)

        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as permission_denied:
            return Response(
                {"error": str(permission_denied)}, status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
