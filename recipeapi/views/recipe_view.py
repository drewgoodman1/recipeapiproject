from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from recipeapi.models.recipe import Recipe
from django.contrib.auth.models import User
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

    def retrieve(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
            serialized = RecipeSerializer(
                recipe, many=False, context={"request": request}
            )
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
            self.check_object_permissions(request, recipe)
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

        # Get the data from the client's JSON payload
        description = request.data.get("description", None)

        # Get the list of ingredients from the request payload
        ingredient_ids = request.data.get("ingredients", [])

        # Create a recipe database row so that there's a pk
        new_recipe = Recipe.objects.create(user=request.user, description=description)

        new_recipe.ingredients.set(ingredient_ids)

        serialized_recipe = RecipeSerializer(new_recipe, context={"request": request})
        return Response(serialized_recipe.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
            self.check_object_permissions(request, recipe)  # Ensure user has permission

            # Get the data from the client's JSON payload
            description = request.data.get("description", None)
            if description:
                recipe.description = description
                recipe.save()

            # Serialize the recipe with the updated data, partial=True allows partial updates
            serializer = RecipeSerializer(
                recipe, data=request.data, partial=True, context={"request": request}
            )

            if serializer.is_valid():
                serializer.save()

            # Update ingredients if provided
            ingredient_ids = request.data.get("ingredients", None)
            if ingredient_ids is not None:
                recipe.ingredients.set(ingredient_ids)

                # Re-serialize the recipe to include the updated ingredients
                serialized_recipe = RecipeSerializer(
                    recipe, context={"request": request}
                )
                return Response(serialized_recipe.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
