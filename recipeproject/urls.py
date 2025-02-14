from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
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
    path("recipes/<int:pk>/favorite", RecipeView.as_view({"post": "favorite"})),
    path("recipes/favorites", RecipeView.as_view({"get": "list_favorites"})),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
