from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet,
                    login, logout)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(v1_router.urls), name='foodgram-api'),
    path('auth/token/login/', login, name='login'),
    path('auth/token/logout/', logout, name='logout'),
]
