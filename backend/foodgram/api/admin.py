from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(UserAdmin):

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'get_followers_count',
        'get_recipes_count',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'first_name',
        'email',
    )

    @admin.display(description='Количество подписчиков')
    def get_followers_count(self, obj):
        return obj.follower.count()

    @admin.display(description='Количество рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = (IngredientInline,)
    list_display = (
        'pub_date',
        'id',
        'name',
        'author',
        'favorite_count',
        'ingredients_list',
        'tags_list',
    )
    search_fields = (
        'name',
        'author',
    )
    list_filter = (
        'tags',
    )

    @admin.display(description='Добавлено в избранное')
    def favorite_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Список ингредиентов')
    def ingredients_list(self, obj):
        return ', '.join(obj.ingredients.values_list('name', flat=True))

    @admin.display(description='Список тегов')
    def tags_list(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True))


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'color_display',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )

    @admin.display(description='Цвет')
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {};">{}</span>',
            obj.color, obj.color
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'measurement_unit',
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = (
        'recipe',
        'ingredient',
    )
    search_fields = (
        'recipe',
        'ingredient'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = (
        'user',
    )
    search_fields = (
        'user',
    )
