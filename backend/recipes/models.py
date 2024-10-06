from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_LENGTH_NAME = 150
MAX_LENGTH_RECIPE = 256
MAX_LENGTH_INGREDIENT = 128
MAX_LENGTH_TAG = 32
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_MEASUERMENT = 64


class HelpText:
    NAME = f"Не более {MAX_LENGTH_NAME} символов"
    USERNAME = (
        f"Максимум {MAX_LENGTH_USERNAME} символов. Допускаются "
        "буквы, цифры и символы @/./+/- ."
    )
    MEASUERMENT = f"Максимум {MAX_LENGTH_MEASUERMENT} символов."
    TAG = f"Не более {MAX_LENGTH_TAG} символов"
    INGREDIENT = f"Не более {MAX_LENGTH_INGREDIENT} символов"
    RECIPE = f"Не более {MAX_LENGTH_RECIPE} символов"


class User(AbstractUser):

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
        help_text=HelpText.NAME,
        blank=False,
    )

    last_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
        help_text=HelpText.NAME,
        blank=False,
    )

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=MAX_LENGTH_USERNAME,
        help_text=HelpText.USERNAME,
        unique=True,
        blank=False,
    )

    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
    )

    avatar = models.ImageField(
        upload_to="users/avatars/", null=True, default=None
    )

    class Meta:
        ordering = ("username",)


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        db_index=True,
    )

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_RECIPE,
        help_text=HelpText.RECIPE,
    )

    image = models.ImageField(
        upload_to="users/avatars/",
        default=None,
        blank=False,
    )

    text = models.TextField(verbose_name="Текст")

    ingredients = models.ManyToManyField(
        "Ingredient", through="RecipeIngredient"
    )

    tags = models.ManyToManyField("Tag", verbose_name="Тэг")

    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
    )

    pub_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ["-pub_at"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name}"


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_TAG,
        help_text=HelpText.INGREDIENT,
    )

    slug = models.SlugField(
        verbose_name="Идентификатор",
        max_length=MAX_LENGTH_TAG,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_INGREDIENT,
        help_text=HelpText.TAG,
        null=False,
        blank=False,
    )

    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LENGTH_MEASUERMENT,
        help_text=HelpText.MEASUERMENT,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингедиенты"

    def __str__(self):
        return f"{self.name}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="uniqueRecipeIngredient"
            ),
        ]

    def __str__(self):
        return f"{self.recipe} {self.ingredient}"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )

    def __str__(self):
        return f"{self.user} {self.recipe}"

    class Meta:
        verbose_name = "Избранный Рецепт"
        verbose_name_plural = "Избранные рецепты"


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="UserToFollowNotIsFollowing",
            ),
            models.UniqueConstraint(
                fields=["user", "following"], name="uniqueUserToFollowing"
            ),
        ]

    def __str__(self):
        return f"{self.user} {self.following}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="cart"
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        unique_together = ("user", "recipe")
