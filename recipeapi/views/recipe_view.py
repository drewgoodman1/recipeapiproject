from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from recipeapi.models.recipe import Recipe
from django.contrib.auth.models import User


class RecipeSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        return self.context["request"].user == obj.user

    class Meta:
        model = Recipe
        fields = ("id", "description", "is_owner")
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
        description = request.data.get("description", None)

        new_recipe = Recipe.objects.create(user=request.user, description=description)

        serialized_recipe = RecipeSerializer(new_recipe, context={"request": request})
        return Response(serialized_recipe.data, status=status.HTTP_201_CREATED)
