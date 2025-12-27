# apps/pokemon/admin.py

from django.contrib import admin
from .models import Pokemon, FavoritePokemon


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_primary', 'type_secondary', 'source', 'created_at']
    list_filter = ['source', 'type_primary', 'created_at']
    search_fields = ['name', 'type_primary', 'type_secondary']
    readonly_fields = ['created_at']


@admin.register(FavoritePokemon)
class FavoritePokemonAdmin(admin.ModelAdmin):
    list_display = ['user', 'pokemon', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'pokemon__name']
    readonly_fields = ['created_at']

