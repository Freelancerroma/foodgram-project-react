from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class RecipesPagination(PageNumberPagination):
    """Переопределенный класс базового пагинатора."""

    page_size_query_param = 'limit'
