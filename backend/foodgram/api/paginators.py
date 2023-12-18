from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class RecipesPagination(PageNumberPagination):
    """Переопределенный класс базового пагинатора - рецепты."""

    page_size_query_param = 'limit'


class IngredientPagination(PageNumberPagination):
    """Переопределенный класс базового пагинатора - ингредиенты."""

    def get_paginated_response(self, data):
        return Response(data)
