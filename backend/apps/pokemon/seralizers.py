# apps/pokemon/seralizers.py

# handle convert database models to JSON and vice versa
from rest_framework import serializers
from .models import Pokemon, FavoritePokemon
from django.contrib.auth.models import User

class PokemonSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Pokemon
        fields = '__all__'
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoritePokemon.objects.filter(
                user = request.user,
                pokemon = obj
            ).exists()
        return False
    
class PokemonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['name', 'type_primary', 'type_secondary', 'latitude', 'longitude', 'location_name', 'sprite', 'moves', 'height', 'weight', 'category', 'abilities', 'stats', 'source', 'uploaded_by']

class FavoritePokemonSerializer(serializers.ModelSerializer):
    pokemon = PokemonSerializer(read_only=True)
    
    class Meta:
        model = FavoritePokemon
        fields = ['id', 'pokemon', 'created_at']