from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from recipeapi.models.recipe import Recipe
from .ingredient_view import IngredientSerializer


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        return self.context["request"].user == obj.user

    class Meta:
        model = Recipe
        fields = ("id", "description", "is_owner", "ingredients")
        depth = 1


class RecipeView(viewsets.ViewSet):
    permission_classes = [
        IsAuthenticated
    ]  # Ensure the user is authenticated for all actions

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
        ingredient_ids = request.data.get("ingredients", [])

        new_recipe = Recipe.objects.create(user=request.user, description=description)
        new_recipe.ingredients.set(ingredient_ids)

        serialized_recipe = RecipeSerializer(new_recipe, context={"request": request})
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
                recipe.save()

            serializer = RecipeSerializer(
                recipe, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()

            ingredient_ids = request.data.get("ingredients", None)
            if ingredient_ids is not None:
                recipe.ingredients.set(ingredient_ids)

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
