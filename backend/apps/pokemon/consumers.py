# apps/pokemon/consumers.py

import json
import asyncio
import random
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import aiohttp
import os
from dotenv import load_dotenv
from .models import Pokemon

load_dotenv()

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
        """Calculate energy based on weather with +/- 20% variance"""
        latitude = self.pokemon.latitude
        longitude = self.pokemon.longitude
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            # Return default energy if API key is not set
            return 100.0
        
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
                        energy_level = self.calculate_energy_based_on_weather(weather_description, temperature)
                        return energy_level
                    else:
                        # Return default energy if API call fails
                        return 100.0
        except Exception:
            # Return default energy on any error
            return 100.0
            
    def calculate_energy_based_on_weather(self, weather_description, temperature):
        """Calculate energy based on weather with +/- 20% variance"""
        
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
            
        # Calculate final energy level
        # +/- 20% variance
        final_energy = base_energy * energy_modifier * random.uniform(0.8, 1.2)
        return max(0, min(final_energy, 100))  # clamp between 0 and 100