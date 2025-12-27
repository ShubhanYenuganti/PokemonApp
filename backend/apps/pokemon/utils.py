# apps/pokemon/utils.py

import requests
from .models import Pokemon
import random
import json

def fetch_pokemon_from_api(limit = 100):
    """Fetch Pokemon from PokeAPI and assign coordinates"""
    
    base_url = "https://pokeapi.co/api/v2/pokemon"
    pokemon_list = []
    
    # Load polyline data (you'll need to parse the A-J and K-Z files)
    polylines = load_polylines()
    
    for i in range(1, limit + 1):
        try:
            response = requests.get(f"{base_url}/{i}")
            data = response.json()
            
            # Determine coordinates based on Pokemon name
            coords = assign_coordinates(data['name'], polylines)
            
            # get moves at level 60
            moves = get_moves_at_level(data['name'], 60)
            
            pokemon = Pokemon(
                name = data['name'].capitalize(),
                latitude = coords['latitude'],
                longitude = coords['longitude'],
                
                type_primary = data['types'][0]['type']['name'],
                type_secondary = data['types'][1]['type']['name'] if len(data['types']) > 1 else '',
                
                moves = moves,
                sprite = data['sprites']['front_default'],
                height = data['height'],
                weight = data['weight'],
                category = data['species']['name'],
                abilities = [ability['ability']['name'] for ability in data['abilities']],
                stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']},
                source = 'API'
            )
            pokemon.save()
            pokemon_list.append(pokemon)
        except Exception as e:
            print(f"Error fetching Pokemon from API: {e}")
            continue

    return pokemon_list

def assign_coordinates(pokemon_name, polylines):
    """Assign coordinates based on first letter and polyline index"""
    
    first_letter = pokemon_name[0].upper()
    
    if first_letter <= 'J':
        polyline = polylines['A-J']
    else:
        polyline = polylines['K-Z']
        
    # Random point within polyline
    return get_random_point_in_polygon(polyline)

def get_random_point_in_polygon(polygon):
    """Get random point within a polyline"""
    # Implementation depends on your polyline format
    # Bsaic bounding box approach for now
    
    lats = [point[0] for point in polygon]
    lngs = [point[1] for point in polygon]
    
    return {
        'lat': random.uniform(min(lats), max(lats)),
        'lng': random.uniform(min(lngs), max(lngs))
    }
    
def get_moves_at_level(moves_data, level):
    """Get 4 most recent moves learned at a specificied level"""
    
    level_moves = []
    for move in moves_data:
        for version_detail in move['version_group_details']:
            if version_detail['level_learned_at'] <= level:
                level_moves.append({
                    'name': move['move']['name'],
                    'level': version_detail['level_learned_at']
                })
                
    # sort by level and get top 4
    level_moves.sort(key = lambda x: x['level'], reverse = True)
    
    # return top 4 moves
    return [m['name'] for m in level_moves[:4]]

def parse_csv_to_pokemon(row, user):
    """Parse CSV row to Pokemon object"""
    
    return Pokemon(
        name = row['Pokemon'],
        latitude = float(row['Lat']),
        longitude = float(row['Long']),
        type_primary = row['Type'],
        location_name = row['Location'],
        moves = json.loads(row.get('Moves', '[]')),
        sprite = row.get('Sprite', ''),
        source = 'CSV',
        uploaded_by = user
    )
    
def load_polylines():
    """Load polyline data from files"""
    polylines = {}
    with open('backend/apps/pokemon/data/polylines_A-J.json', 'r') as f:
        polylines['A-J'] = json.load(f)
    with open('backend/apps/pokemon/data/polylines_K-Z.json', 'r') as f:
        polylines['K-Z'] = json.load(f)
    return polylines