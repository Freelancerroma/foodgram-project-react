from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from recipes.models import Favorite, ShoppingCart
from users.models import Follow


class AddDeleteMixin:
    """Миксин создания и удаления связей между объектами."""

    handlers = {
        'follow': {
            'model': Follow,
            'fields': ['following_id'],
            'error_message': 'Вы уже подписаны на автора.',
            'extra_params': 'many'
        },
        'favorite': {
            'model': Favorite,
            'fields': ['recipe_id'],
            'error_message': 'Вы уже добавили этот рецепт в избранное.'
        },
        'cart': {
            'model': ShoppingCart,
            'fields': ['recipe_id'],
            'error_message': 'Вы уже добавили этот рецепт в корзину.'
        }
    }

    def add_relation(self, id, handler, serializer):
        user = self.request.user
        relation = self.handlers[handler]
        create_obj = relation['model']
        to_relation = relation['fields']
        if handler in ['favorite', 'cart']:
            try:
                from_id = self.queryset.filter(id=id).get()
            except self.queryset.model.DoesNotExist:
                return JsonResponse(
                    {'error': 'Bad Request'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        from_id = get_object_or_404(self.queryset, id=id)

        if handler == 'follow' and from_id == user:
            error = 'Нельзя подписаться на самого себя.'
            return Response(
                error,
                status=status.HTTP_400_BAD_REQUEST
            )

        as_key = dict.fromkeys(to_relation, from_id.id)
        new_obj, create = create_obj.objects.get_or_create(
            user=user,
            **as_key
        )
        if not create:
            error = relation['error_message']
            return Response(
                error,
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'extra_params' in relation:
            serializer = serializer(
                new_obj, context={'request': self.request}
            )
        else:
            serializer = serializer(from_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, id, handler):
        relation = self.handlers[handler]
        create_obj = relation['model']
        from_id = get_object_or_404(self.queryset, id=id)
        as_key = dict.fromkeys(relation['fields'], from_id.id)
        try:
            get_object_or_404(
                create_obj, user=self.request.user,
                **as_key
            ).delete()
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet для методов Get, List, Create, Retrieve."""

    lookup_field = 'id'
