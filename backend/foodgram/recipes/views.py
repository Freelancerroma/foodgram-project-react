from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeInListSerializer
)
from .models import Tag, Ingredient, Recipe, RecipeIngredient
from rest_framework import viewsets, filters, permissions
from users.permissions import AuthorOrRead
from .mixins import AddDeleteMixin
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """VieSet для тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter)
    search_fields = ('name', '^name')


class RecipeViewSet(AddDeleteMixin, viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = (AuthorOrRead,)
    ordering_fields = ('-pub_date',)

    def get_serializer_class(self):
        return (
            RecipeReadSerializer
            if self.request.method in permissions.SAFE_METHODS
            else RecipeWriteSerializer
        )

    @action(
        methods=['post'],
        detail=True,
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_favorite(self, request, id):
        return self.add_relation(id, 'favorite', RecipeInListSerializer)

    @user_favorite.mapping.delete
    def delete_favorite(self, request, id):
        return self.delete_relation(id, 'favorite')

    @action(
        methods=['post'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_cart(self, request, id):
        return self.add_relation(id, 'cart', RecipeInListSerializer)

    @user_cart.mapping.delete
    def delete_cart(self, request, id):
        return self.delete_relation(id, 'cart')

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_cart(self, request):
        cart = (RecipeIngredient.objects
                .filter(recipe__cart__user=request.user)
                .order_by('ingredient__name')
                .values('ingredient__name', 'ingredient__measure_unit')
                .annotate(amount=Sum('amount')))
        content = '\n'.join(
            [
                (
                    f'{ol}. {ingredient["ingredient__name"]} '
                    f'{ingredient["amount"]} '
                    f'{ingredient["ingredient__measure_unit"]}'
                ) for ol, ingredient in enumerate(list(cart), start=1)
            ]
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response
