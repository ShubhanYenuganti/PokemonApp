# apps/pokemon/consumers.py

import json
import asyncio
import random
import math
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import aiohttp
import os
from pathlib import Path
from dotenv import load_dotenv
from .models import Pokemon

# Load .env from the main project directory (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

# Load polylines once at module level
POLYLINES = None

def load_polylines():
    """Load polyline data from files"""
    global POLYLINES
    if POLYLINES is None:
        POLYLINES = {}
        polyline_dir = Path(__file__).resolve().parent / 'data'
        with open(polyline_dir / 'polylines_A-J.json', 'r') as f:
            POLYLINES['A-J'] = json.load(f)
        with open(polyline_dir / 'polylines_K-Z.json', 'r') as f:
            POLYLINES['K-Z'] = json.load(f)
    return POLYLINES

def get_polyline_for_pokemon(pokemon_name):
    """Get the appropriate polyline based on pokemon name's first letter"""
    first_letter = pokemon_name[0].upper()
    polylines = load_polylines()
    
    if first_letter <= 'J':
        return polylines['A-J']
    else:
        return polylines['K-Z']

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on Earth (in km)"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def point_to_line_distance(point_lat, point_lon, line_start_lat, line_start_lon, 
                            line_end_lat, line_end_lon):
    """Calculate the distance from a point to a line segment (in km) using spherical geometry"""
    # For short line segments, sample points along the line and find minimum distance
    # This is more accurate for spherical geometry than linear interpolation
    
    # Calculate distance to endpoints
    dist_start = haversine_distance(point_lat, point_lon, line_start_lat, line_start_lon)
    dist_end = haversine_distance(point_lat, point_lon, line_end_lat, line_end_lon)
    
    # If line segment is very short, just use the minimum endpoint distance
    segment_length = haversine_distance(line_start_lat, line_start_lon, line_end_lat, line_end_lon)
    if segment_length < 0.1:  # Less than 100m
        return min(dist_start, dist_end)
    
    # Sample points along the line segment to find closest point
    # Use 10 samples for accuracy
    min_distance = min(dist_start, dist_end)
    num_samples = 10
    
    for i in range(1, num_samples):
        t = i / num_samples
        # Interpolate latitude and longitude
        sample_lat = line_start_lat + t * (line_end_lat - line_start_lat)
        sample_lon = line_start_lon + t * (line_end_lon - line_start_lon)
        
        # Calculate distance to this sample point
        dist = haversine_distance(point_lat, point_lon, sample_lat, sample_lon)
        min_distance = min(min_distance, dist)
    
    return min_distance

def is_point_near_polyline(point_lat, point_lon, polyline_data, max_distance_km=1.0):
    """Check if a point is near any segment of a MultiLineString polyline"""
    if not polyline_data or 'coordinates' not in polyline_data:
        return False
    
    coordinates = polyline_data['coordinates']
    
    # Check each line string in the MultiLineString
    for line_string in coordinates:
        # Check each segment in the line string
        for i in range(len(line_string) - 1):
            start = line_string[i]
            end = line_string[i + 1]
            
            # Coordinates are [longitude, latitude]
            start_lon, start_lat = start[0], start[1]
            end_lon, end_lat = end[0], end[1]
            
            # Calculate distance from point to line segment
            distance = point_to_line_distance(
                point_lat, point_lon,
                start_lat, start_lon,
                end_lat, end_lon
            )
            
            if distance <= max_distance_km:
                return True
    
    return False

class PokemonEnergyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pokemon_id = self.scope['url_route']['kwargs']['pokemon_id']
        await self.accept()
        
        # Verify pokemon exists
        pokemon = await self.get_pokemon(self.pokemon_id)
        if not pokemon:
            await self.close(code=4004)
            return
        
        self.pokemon = pokemon
        # Start sending energy updates
        self.update_task = asyncio.create_task(self.send_energy_updates())
    
    async def disconnect(self, close_code):
        # Cancel the update task when client disconnects
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
    
    @database_sync_to_async
    def get_pokemon(self, pokemon_id):
        """Get pokemon from database"""
        try:
            return Pokemon.objects.get(id=pokemon_id)
        except Pokemon.DoesNotExist:
            return None
    
    async def send_energy_updates(self):
        """Send energy updates to the client"""
        while True:
            try:
                # Calculate energy based on weather
                energy_level = await self.calculate_energy_level()
                
                await self.send(text_data=json.dumps({
                    'energy_level': energy_level,
                    'timestamp': datetime.now().isoformat()
                }))
                
                await asyncio.sleep(5)  # update every 5 seconds
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'error': str(e)
                }))
                await asyncio.sleep(5)
    
    async def calculate_energy_level(self):
        """Calculate energy based on weather with +/- 20% variance and polyline proximity"""
        latitude = self.pokemon.latitude
        longitude = self.pokemon.longitude
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Check if pokemon is near appropriate polyline
        polyline_data = get_polyline_for_pokemon(self.pokemon.name)
        is_near_polyline = is_point_near_polyline(latitude, longitude, polyline_data, max_distance_km=1.0)
        
        # Apply polyline proximity modifier
        polyline_modifier = 1.0
        if not is_near_polyline:
            # Reduce energy if pokemon is not near its designated polyline
            polyline_modifier = 0.85  # -15% energy if not near polyline
        
        if not api_key:
            # Return default energy with polyline modifier if API key is not set
            return 100.0 * polyline_modifier
        
        # Fetch weather from OpenWeatherMap API
        try:
            async with aiohttp.ClientSession() as session:
                url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric'
                async with session.get(url) as response:
                    if response.status == 200:
                        weather_data = await response.json()
                        
                        # Extract weather conditions
                        weather_description = weather_data['weather'][0]['description']
                        temperature = weather_data['main']['temp']
                        
                        # Calculate energy based on weather
                        energy_level = self.calculate_energy_based_on_weather(
                            weather_description, temperature, polyline_modifier
                        )
                        return energy_level
                    else:
                        # Return default energy with polyline modifier if API call fails
                        return 100.0 * polyline_modifier
        except Exception:
            # Return default energy with polyline modifier on any error
            return 100.0 * polyline_modifier
            
    def calculate_energy_based_on_weather(self, weather_description, temperature, polyline_modifier=1.0):
        """Calculate energy based on weather with +/- 20% variance and polyline proximity"""
        
        # Base energy level (100)
        base_energy = 100
        
        # Weather energy modifiers
        if 'rain' in weather_description.lower():
            energy_modifier = 0.8  # -20% energy
        elif 'snow' in weather_description.lower():
            energy_modifier = 0.9  # -10% energy
        else:
            energy_modifier = 1.0  # no change
            
        # Temperature energy modifiers
        if temperature < 0:
            energy_modifier *= 0.9  # -10% energy
        elif temperature > 30:
            energy_modifier *= 1.1  # +10% energy
        
        # Apply polyline modifier
        energy_modifier *= polyline_modifier
            
        # Calculate final energy level
        # +/- 20% variance
        final_energy = base_energy * energy_modifier * random.uniform(0.8, 1.2)
        return max(0, min(final_energy, 100))  # clamp between 0 and 100