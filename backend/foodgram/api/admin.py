from django.contrib import admin
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
)
from users.models import User
from django.contrib.auth.admin import UserAdmin
admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(UserAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "first_name",
        "email",
    )


class IngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = (IngredientInline,)
    list_display = (
        'pub_date',
        'id',
        'name',
        'author',
        'favorite_count',
    )
    search_fields = (
        'name',
        'author',
    )
    list_filter = (
        'tags',
    )

    def favorite_count(self, obj):
        return obj.favorites.count()


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
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'measure_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'measure_unit',
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
