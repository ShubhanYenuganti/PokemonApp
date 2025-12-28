# apps/pokemon/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pokemon, FavoritePokemon
from .serializers import PokemonSerializer, PokemonCreateSerializer
from .utils import fetch_pokemon_from_api, parse_csv_to_pokemon
import csv
import io

class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'type_primary', 'type_secondary', 'category']
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    @action(detail=False, methods=['post'])
    def fetch_from_api(self, request):
        """Fetch 100 Pokemon from PokeAPI"""
        try:
            # fetch_pokemon_from_api returns Pokemon model instances (already saved)
            pokemon_list = fetch_pokemon_from_api(limit=100)
            
            # Serialize the saved Pokemon instances
            serializer = PokemonSerializer(pokemon_list, many=True, context={'request': request})
            
            return Response({
                'message': f'Successfully fetched {len(pokemon_list)} Pokemon',
                'count': len(pokemon_list),
                'results': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'])
    def upload_from_csv(self, request):
        """Upload Pokemon from CSV file"""
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({
                'error': 'No CSV file provided'
            }, status = status.HTTP_400_BAD_REQUEST)
        try:
            # Read CSV
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            pokemon_list = []
            for row in csv_data:
                pokemon = parse_csv_to_pokemon(row, request.user)
                pokemon_list.append(pokemon)
            
            # bulk create
            Pokemon.objects.bulk_create(pokemon_list)
            
            serializer = PokemonSerializer(pokemon_list, many=True, context={'request': request})
            
            return Response({
                'message': f'Successfully uploaded {len(pokemon_list)} Pokemon',
                'count': len(pokemon_list),
                'results': serializer.data
            }, status = status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail = True, methods=['post'])
    def favorite(self, request, pk = None):
        """Add or remove Pokemon from favorites"""
        pokemon = self.get_object()
        favorite, created = FavoritePokemon.objects.get_or_create(
            user = request.user,
            pokemon = pokemon
        )
        
        if not created:
            favorite.delete()
            return Response({
                'message': 'Pokemon removed from favorites'
            }, status = status.HTTP_200_OK)
            
        return Response({
            'message': 'Pokemon added to favorites',
        }, status = status.HTTP_201_CREATED)
    
    @action(detail = False, methods=['get'])
    def favorites(self, request):
        """Get list of favorite Pokemon"""
        favorites = FavoritePokemon.objects.filter(
            user = request.user
        ).select_related('pokemon')
        
        pokemon = [favorite.pokemon for favorite in favorites]
        
        serializer = PokemonSerializer(pokemon, many = True, context = {'request': request})
        
        return Response({
            'message': 'Successfully fetched list of favorite Pokemon',
            'count': len(favorites),
            'results': serializer.data
        }, status = status.HTTP_200_OK)