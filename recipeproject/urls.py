from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipeapi.views import UserViewSet
from recipeapi.views.recipe_view import RecipeView
from recipeapi.views.ingredient_view import IngredientView

router = DefaultRouter(trailing_slash=False)
router.register(r"recipes", RecipeView, basename="recipe")
router.register(r"ingredients", IngredientView, basename="ingredient")

urlpatterns = [
    path("", include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
]
