import base64
import re

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, User


class FavoriteAndShoppingCartMixin:
    """mixin for is_favorited and is_in_shopping_cart fields."""

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj.id).exists()
        )


class IsSubscribedMixin:
    """mixin for is_subscribed field."""

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return user.following.filter(following=obj).exists()
        return False


class Base64ImageField(serializers.ImageField):
    """mixin for convert images fields."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)

    def to_representation(self, value):
        if value:
            with open(value.path, "rb") as image_file:
                return (
                    "data:image/jpeg;base64,"
                    + base64.b64encode(image_file.read()).decode()
                )
        return None


class AvatarSerializer(serializers.ModelSerializer):
    """avatar serializer."""

    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "avatar",
        ]


class TagSerializer(serializers.ModelSerializer):
    """tag serializer."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """basic ingredient model serializer."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeMiniSerializer(serializers.ModelSerializer):
    """basic recipe fields serializer."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class CustomAuthTokenSerializer(serializers.Serializer):
    """custom token serializr."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Пользователь с таким email не найден"
            )
        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError("Неверные учетные данные")

        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """basic user model serializer."""

    username = serializers.RegexField(
        regex=r"^[\w.@+-]+$",
        error_messages={
            "invalid": "username failed. only alph, digits and .@+-"
        },
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Это имя пользователя уже занято. Пожалуйста, выберите другое."
            )
        if not re.match(r"^[\w.@+-]+$", value):
            raise serializers.ValidationError(
                "Username не соответствует регулярному выражению."
            )
        if len(value) >= 150:
            raise serializers.ValidationError(
                "Максимальная длина username - 150 символов"
            )
        return value


class UserWithSubscriptionsSerializer(
    serializers.ModelSerializer, IsSubscribedMixin
):
    """user with his subscriptions serializer."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        ]

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class UserWithRecipesSerializer(
    serializers.ModelSerializer, IsSubscribedMixin
):
    """user with recipes serializer."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes_qs = Recipe.objects.filter(author=obj)
        if recipes_limit:
            recipes_qs = recipes_qs[: int(recipes_limit)]
        return RecipeMiniSerializer(recipes_qs, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ingredient in recipes serializer."""

    ingredient = IngredientSerializer(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all(), write_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "ingredient", "amount")

    def to_representation(self, instance):
        return {
            "id": instance.ingredient.id,
            "name": instance.ingredient.name,
            "measurement_unit": instance.ingredient.measurement_unit,
            "amount": instance.amount,
        }


class RecipeSerializer(
    serializers.ModelSerializer, FavoriteAndShoppingCartMixin
):
    """full Recipe serializer for read."""

    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    author = UserWithSubscriptionsSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="recipeingredient_set", many=True, read_only=True
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )


class RecipeCreateUpdateSerializer(
    serializers.ModelSerializer, FavoriteAndShoppingCartMixin
):
    """full Recipe serializer for POST and UPDATE."""

    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    author = UserWithSubscriptionsSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source="recipeingredient_set"
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipeingredient_set", [])
        tags_data = validated_data.pop("tags", None)

        self._validate_tags_ingredients_data(ingredients_data, tags_data)

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data["ingredient"]
            amount = ingredient_data["amount"]
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):

        ingredients_data = validated_data.pop("recipeingredient_set", None)
        tags_data = validated_data.pop("tags", None)

        self._validate_tags_ingredients_data(ingredients_data, tags_data)

        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )

        if tags_data:
            instance.tags.set(tags_data)

        if ingredients_data:
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                ingredient = ingredient_data["ingredient"]
                amount = ingredient_data["amount"]
                RecipeIngredient.objects.create(
                    recipe=instance, ingredient=ingredient, amount=amount
                )

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return representation

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не менее 1 минуты."
            )
        return value

    def _validate_tags_ingredients_data(self, ingredients_data, tags_data):
        if ingredients_data is None or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно."}
            )

        ingredient_ids = [
            ingredient["ingredient"] for ingredient in ingredients_data
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):

            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )

        if tags_data is None or len(tags_data) == 0:
            raise serializers.ValidationError(
                {"tags": "Это поле обязательно."}
            )

        tags_slugs = [tag.slug for tag in tags_data]
        if len(tags_data) != len(set(tags_slugs)):
            raise serializers.ValidationError(
                {"tags": "Тэги не должны повторяться."}
            )

        for ingredient in ingredients_data:
            amount = ingredient.get("amount")
            if amount is None or amount < 1:
                raise serializers.ValidationError(
                    {
                        "ingredients": ("Количество ингредиент"
                                        "должно быть больше 0.")
                    }
                )
