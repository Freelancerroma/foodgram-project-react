from foodgram import settings
from rest_framework import serializers
from recipes.models import Recipe
from .models import User, Follow
from recipes.serializers import RecipeInListSerializer


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
        read_only_fields = '__all__'

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
