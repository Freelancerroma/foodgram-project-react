from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram import settings
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed',
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = '__all__'

    def get_is_subscribed(self, obj):
        follower = self.context.get('request').user
        if follower.is_anonymous:
            return False
        return Follow.objects.filter(
            user=follower,
            following=obj
        ).exists()


class UserRegistrationSerializer(UserSerializer):
    """Сериализатор регистрации пользователя."""

    first_name = serializers.CharField(
        required=True,
        max_length=settings.FIRST_NAME_LEN,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=settings.LAST_NAME_LEN,
    )
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_LEN,
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_LEN,
    )
    password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа."""

    password = serializers.CharField(
        max_length=settings.PASSWORD_LEN,
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_LEN,
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля."""

    new_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
    )
    current_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
    )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measure_unit',
        )
        read_only_fields = ('__all__',)


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measure_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measure_unit',
            'amount',
        )
        read_only_fields = ('__all__',)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(many=True,)
    author = UserSerializer()
    image = Base64ImageField()
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.carts.filter(recipe=obj).exists()
        )


class RecipeInListSerializer(serializers.ModelSerializer):
    """Сериализатор с кратким отображением рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('__all__',)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        source='recipe_ingredients',
    )
    text = serializers.CharField(
        required=True,
    )
    cooking_time = serializers.IntegerField(
        required=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredients = RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            )
            print(ingredient)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeInListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count',
    )

    class Meta:
        model = Follow
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_recipes_count(self, following):
        return following.author.recipes.count()

    def get_recipes(self, following):
        recipes = (Recipe.objects.filter(author=following.author))
        serializer = RecipeInListSerializer(
            recipes,
            many=True,
            read_only=True,
            context={'request': self.context.get('request')},
        )
        return serializer.data
