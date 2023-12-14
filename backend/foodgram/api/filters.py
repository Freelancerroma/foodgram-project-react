from rest_framework import filters
import django_filters
from recipes.models import Recipe


class IngredientFilter(filters.SearchFilter):
    """Фильтр поиска ингредиента по имени."""

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    """Фильтр поиска рецептов."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        return (
            queryset.filter(favorite__user=self.request.user)
            if value and not self.request.user.is_anonymous
            else queryset
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return (
            queryset.filter(cart__user=self.request.user)
            if value and not self.request.user.is_anonymous
            else queryset
        )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
