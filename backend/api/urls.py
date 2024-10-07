from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomAuthToken, IngredientViewSet, LogoutView,
                    RecipeViewSet, TagViewSet, UserViewSet)

router_v1 = DefaultRouter()

router_v1.register("tags", viewset=TagViewSet, basename="tags")

router_v1.register(
    "ingredients", viewset=IngredientViewSet, basename="ingredients"
)

router_v1.register("recipes", viewset=RecipeViewSet, basename="recipes")


router_v1.register(r"users", UserViewSet, basename="users")

url_auth = [
    path("token/login/", CustomAuthToken.as_view(), name="token_obtain"),
    path("token/logout/", LogoutView.as_view(), name="logout"),
]


urlpatterns = [
    path("auth/", include(url_auth)),
    path("", include(router_v1.urls)),    
]
