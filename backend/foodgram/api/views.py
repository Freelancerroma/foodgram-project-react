from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User
from users.permissions import AuthorOrRead

from .filters import IngredientFilter, RecipeFilter
from .mixins import AddDeleteMixin, ListCreateRetrieveViewSet
from .paginators import IngredientPagination, RecipesPagination
from .serializers import (ChangePasswordSerializer, FollowSerializer,
                          IngredientSerializer, RecipeInListSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, UserLoginSerializer,
                          UserRegistrationSerializer, UserSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """VieSet для тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = IngredientPagination


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = IngredientPagination


class RecipeViewSet(AddDeleteMixin, viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = (AuthorOrRead,)
    ordering_fields = ('-pub_date',)
    pagination_class = RecipesPagination
    filterset_class = RecipeFilter

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
        cart = (
            RecipeIngredient.objects
            .filter(recipe__carts__user=request.user)
            .order_by('ingredient__name')
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        content = '\n'.join(
            [
                (
                    f'{ol}. {ingredient["ingredient__name"]} '
                    f'{ingredient["amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}'
                ) for ol, ingredient in enumerate(list(cart), start=1)
            ]
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class UserViewSet(AddDeleteMixin, ListCreateRetrieveViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = RecipesPagination

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_subscriptions(self, request):
        user = request.user
        following = user.follower.all()
        serializer = FollowSerializer(
            self.paginate_queryset(following), many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_subscribe(self, request, id):
        return self.add_relation(id, 'follow', FollowSerializer)

    @user_subscribe.mapping.delete
    def delete_subscribtion(self, request, id):
        return self.delete_relation(id, 'follow')

    @action(
        methods=['post'],
        detail=False,
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(
            serializer.validated_data.get('current_password')
        ):
            return Response(
                'Неверный пароль.',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        get_user_model(),
        email=serializer.validated_data.get('email')
    )
    if not user.check_password(serializer.validated_data.get('password')):
        return Response(
            {'message': 'Неверный пароль'},
            status=status.HTTP_400_BAD_REQUEST
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {'auth_token': str(token)},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
