import csv
from collections import defaultdict

import short_url
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag, User)
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .mixins import DefaultIngredientTagMixin
from .pagination import (PageNumberPaginationDataOnly,
                         UserSubscriptionPagination)
from .serializers import (AvatarSerializer, CustomAuthTokenSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeMiniSerializer, RecipeSerializer,
                          TagSerializer, UserSerializer,
                          UserWithRecipesSerializer,
                          UserWithSubscriptionsSerializer)

BASE_URL = 'https://tonenkovfoodgram'


def redirect_to_full_link(request, short_code):
    """View для перенаправления короткой ссылки на полный URL рецепта."""
    try:
        recipe_id = short_url.decode_url(short_code)
        recipe = get_object_or_404(Recipe, id=recipe_id)

        full_url = f"{BASE_URL}/recipes/{recipe.id}/"

        return HttpResponseRedirect(full_url)

    except (ValueError, Recipe.DoesNotExist):
        return HttpResponse(
            "Invalid short code or recipe not found", status=404
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(DefaultIngredientTagMixin):
    """Tag view set."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(DefaultIngredientTagMixin):
    """Ingredient view set."""

    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPaginationDataOnly


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key})


class UserViewSet(viewsets.ModelViewSet):
    """
    user/ view set.

    actions:
        me
        set_avatar
        set_password
        subscriptions
        subscribe
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = UserSubscriptionPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "me"]:
            return UserWithSubscriptionsSerializer
        return UserSerializer

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def set_avatar(self, request):
        """Action for set user's avatar."""
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if request.method == "PUT":

            if "avatar" in request.data:
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {"avatar": user.avatar.url}, status=status.HTTP_200_OK
                    )
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detail": "файл для обновления аватара not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
        url_path="set_password",
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        """Action for set user's password."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"detail": "Требуется указать текущий и новый пароль."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"detail": "Текущий пароль неверный."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Пароль успешно изменен."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """Action get subscibions list."""
        subscriptions = Subscription.objects.filter(user=request.user)
        users = [sub.following for sub in subscriptions]

        paginated_users = self.paginate_queryset(users)
        serializer = UserWithRecipesSerializer(
            paginated_users, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """Action for subscibe: POST and DELETE methods."""
        user_to_action = get_object_or_404(User, pk=pk)

        if request.method == "POST":
            user_to_action = get_object_or_404(User, pk=pk)

            if Subscription.objects.filter(
                user=request.user, following=user_to_action
            ).exists():
                return Response(
                    {"detail": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.user == user_to_action:
                return Response(
                    {"detail": "Нельзя подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(
                user=request.user, following=user_to_action
            )
            serializer = UserWithRecipesSerializer(
                user_to_action, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            user=request.user, following=user_to_action
        )

        if not subscription.exists():
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(viewsets.ModelViewSet):
    """all recipes actions view set."""

    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter
    permission_class = permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Вы не можете редактировать чужой рецепт.")
        serializer.save()

    @action(
        detail=True,
        methods=["get"],
        url_path="get-link",
        permission_classes=[permissions.AllowAny],
    )
    def get_short_link(self, request, pk=None):
        """Action for getting a short link to the recipe."""
        recipe = get_object_or_404(Recipe, pk=pk)

        encoded_id = short_url.encode_url(recipe.id)

        base_url = "https://tonenkovfoodgram"

        short_link = f"{base_url}/r/{encoded_id}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_to_favorite(self, request, pk=None):
        """
        Action for add recipe for favorites user's list.

        POST and DELETE methods
        """
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":

            if user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {"detail": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = user.favorites.filter(recipe=recipe).first()
        if not favorite:
            return Response(
                {"detail": "Рецепт не найден в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=["delete", "post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def manage_shopping_cart(self, request, pk=None):
        """
        Action for manage a shopping cart.

        POST and DELETE recipes in shopping cart
        """
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "Recipe already in shopping cart"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if cart_item.exists():
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Recipe not found in shopping cart"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=False,
        url_path="download_shopping_cart",
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart_csv(self, request):
        user = request.user
        ingredients = defaultdict(int)

        for cart_item in user.shopping_cart.all():
            recipe = cart_item.recipe
            for recipe_ingredient in recipe.recipeingredient_set.all():
                ingredients[
                    (
                        recipe_ingredient.ingredient.name,
                        recipe_ingredient.ingredient.measurement_unit,
                    )
                ] += recipe_ingredient.amount

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["Ingredient", "Measurement Unit", "Amount"])
        for (ingredient_name, measurement_unit), amount in ingredients.items():
            writer.writerow([ingredient_name, measurement_unit, amount])

        return response

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(
                {"detail": "У вас нет прав для удаления этого рецепта."},
                status=403,
            )
        return super().destroy(request, *args, **kwargs)
