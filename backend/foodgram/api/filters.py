import django_filters
from rest_framework import filters

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
        method='filter_is_favorited_or_in_cart'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_favorited_or_in_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited_or_in_cart(self, queryset, name, value):
        filter_dict = {}
        if name == 'is_favorited':
            filter_dict = {'favorites__user': self.request.user}
        elif name == 'is_in_shopping_cart':
            filter_dict = {'carts__user': self.request.user}

        if value and not self.request.user.is_anonymous:
            queryset = queryset.filter(**filter_dict)

        return queryset
