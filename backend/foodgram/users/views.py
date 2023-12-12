from .mixins import ListCreateRetrieveViewSet
from .models import User
from recipes.mixins import AddDeleteMixin
from .serializers import (
    UserSerializer,
    FollowSerializer,
    ChangePasswordSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


class UserViewSet(AddDeleteMixin, ListCreateRetrieveViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

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
            'Пароль изменен',
            status=status.HTTP_200_OK
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
        return Response('Неверный пароль', status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'auth_token': str(token)}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
