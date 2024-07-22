from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from recipeapi.models.ingredient import Ingredient


# Serializer for Ingredient
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


# ViewSet for Ingredient
class IngredientView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        try:
            ingredient = Ingredient.objects.get(pk=pk)
            serialized = IngredientSerializer(ingredient, many=False)
            return Response(serialized.data, status=status.HTTP_200_OK)
        except Ingredient.DoesNotExist:
            return Response(
                {"error": "Ingredient not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request):
        ingredients = Ingredient.objects.all()
        serialized = IngredientSerializer(ingredients, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            ingredient = Ingredient.objects.get(pk=pk)
            serializer = IngredientSerializer(
                ingredient, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Ingredient.DoesNotExist:
            return Response(
                {"error": "Ingredient not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            ingredient = Ingredient.objects.get(pk=pk)
            ingredient.delete()
            return Response(
                {"message": f"Ingredient {pk} was removed"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Ingredient.DoesNotExist:
            return Response(
                {"error": "Ingredient not found"}, status=status.HTTP_404_NOT_FOUND
            )
