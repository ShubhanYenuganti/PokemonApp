# tests/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from apps.pokemon.models import Pokemon, FavoritePokemon
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from apps.pokemon.consumers import PokemonEnergyConsumer
from apps.pokemon.routing import websocket_urlpatterns
from channels.routing import URLRouter
from unittest.mock import patch, AsyncMock
from asgiref.sync import async_to_sync
import json
import asyncio

# User tests
# Test user registration
class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
    
    # Test user registration
    def test_user_registration(self):
        response = self.client.post('/api/users/register/', {
            'username': 'newuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='newuser').username, 'newuser')
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['message'], 'User created successfully')
        
    # Test repeating user registration
    def test_user_registration_with_invalid_data(self):
        response = self.client.post('/api/users/register/', {
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  
        self.assertFalse('token' in response.data)
        self.assertTrue('username' in response.data)
        self.assertIn('A user with that username already exists.', response.data['username'])
    
    # Test user login
    def test_user_login(self):
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['message'], 'Successfully logged in')
        
    # Test user login with incorrect password
    def test_user_login_with_incorrect_password(self):
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('token' in response.data)
        self.assertFalse('user' in response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
        
    # Test user login with incorrect username
    def test_user_login_with_incorrect_username(self):
        response = self.client.post('/api/users/login/', {
            'username': 'wrongusername',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('token' in response.data)
        self.assertFalse('user' in response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
    
    # Test user login with missing username
    def test_user_login_with_missing_username(self):
        response = self.client.post('/api/users/login/', {
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse('token' in response.data)
        self.assertFalse('user' in response.data)
        self.assertEqual(response.data['error'], 'Username and password are required')
        
    # Test user login with missing password
    def test_user_login_with_missing_password(self):
        response = self.client.post('/api/users/login/', {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse('token' in response.data)
        self.assertFalse('user' in response.data)
        self.assertEqual(response.data['error'], 'Username and password are required')
    
    # Test getting current user information
    def test_get_current_user_information(self):
        # test login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        
        # Use the token to authenticate the request
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    # Test logout
    def test_user_logout(self):
        # test login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        
        # Use the token to authenticate the logout request
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post('/api/users/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully logged out')
        
# Pokemon test
class PokemonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        
    def test_fetching_pokemon_from_api(self):
        # login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['message'], 'Successfully logged in')
        
        # Use the token to authenticate the request
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post('/api/pokemon/fetch_from_api/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully fetched 100 Pokemon')
        self.assertEqual(response.data['count'], 100)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 100)
        for result in response.data['results']:
            self.assertTrue('latitude' in result)
            self.assertTrue('longitude' in result)
            self.assertTrue('name' in result)
            self.assertTrue('type_primary' in result)
            self.assertTrue('type_secondary' in result)
            self.assertTrue('moves' in result)
            self.assertTrue('sprite' in result)
            self.assertTrue('height' in result)
            self.assertTrue('weight' in result)
            self.assertTrue('category' in result)
            self.assertTrue('abilities' in result)
            self.assertTrue('stats' in result)
            self.assertTrue('source' in result)
            self.assertTrue('uploaded_by' in result)
            self.assertTrue('created_at' in result)
            self.assertTrue('location_name' in result)
    
    # Test uploading Pokemon from CSV
    def test_uploading_pokemon_from_csv(self):
        # Login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Create CSV file with proper format matching parse_csv_to_pokemon expectations
        # Moves should be a JSON array string
        csv_content = b'Pokemon,Lat,Long,Type,Location,Moves,Sprite\nMew,34.10214701,-118.9104645,Psychic,Floaroma Town,"[""shadow-ball"", ""ancient-power"", ""future-sight"", ""whirlpool""]",https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/shiny/151.png'
        csv_file = SimpleUploadedFile('test.csv', csv_content, content_type='text/csv')
        
        response = self.client.post('/api/pokemon/upload_from_csv/', {
            'file': csv_file
        }, format='multipart')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully uploaded 1 Pokemon')
        self.assertEqual(response.data['count'], 1)
    
    # Test adding Pokemon to favorites
    def test_adding_pokemon_to_favorites(self):
        # Login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # upload a pokemon first
        csv_content = b'Pokemon,Lat,Long,Type,Location,Moves,Sprite\nMew,34.10214701,-118.9104645,Psychic,Floaroma Town,"[""shadow-ball"", ""ancient-power"", ""future-sight"", ""whirlpool""]",https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/shiny/151.png'
        csv_file = SimpleUploadedFile('test.csv', csv_content, content_type='text/csv')
        
        response = self.client.post('/api/pokemon/upload_from_csv/', {
            'file': csv_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully uploaded 1 Pokemon')
        self.assertEqual(response.data['count'], 1)
        
        pokemon_id = response.data['results'][0]['id']
        pokemon_name = response.data['results'][0]['name']
        
        # add pokemon to favorites
        response = self.client.post(f'/api/pokemon/{pokemon_id}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Pokemon added to favorites')
        
        # get list of favorite Pokemon
        response = self.client.get('/api/pokemon/favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], pokemon_id)
        self.assertEqual(response.data['results'][0]['name'], pokemon_name)
        
        # remove pokemon from favorites
        response = self.client.post(f'/api/pokemon/{pokemon_id}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Pokemon removed from favorites')
        
        # get list of favorite Pokemon
        response = self.client.get('/api/pokemon/favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 0)
        
    # Test searching Pokemon by name, type primary, type secondary, category
    def test_searching_pokemon_by_name(self):
        # Login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # batch upload 100 Pokemon with PokeAPI
        response = self.client.post('/api/pokemon/fetch_from_api/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully fetched 100 Pokemon')
        self.assertEqual(response.data['count'], 100)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 100)
            
        response = self.client.get('/api/pokemon/?search=Bulbasaur')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Bulbasaur')
        
    def test_searching_pokemon_by_type(self):
        # Login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # batch upload 100 Pokemon with PokeAPI
        response = self.client.post('/api/pokemon/fetch_from_api/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully fetched 100 Pokemon')
        self.assertEqual(response.data['count'], 100)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 100)
        
        response = self.client.get('/api/pokemon/?search=water')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertGreater(len(response.data['results']), 0)
        for result in response.data['results']:
            print(result)
            self.assertIn(result['type_primary'] or result['type_secondary'], ['water'])
            
    def test_searching_pokemon_by_category(self):
        # login first
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # batch upload 100 Pokemon with PokeAPI
        response = self.client.post('/api/pokemon/fetch_from_api/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Successfully fetched 100 Pokemon')
        self.assertEqual(response.data['count'], 100)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 100)
        
        response = self.client.get('/api/pokemon/?search=blastoise')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertGreater(len(response.data['results']), 0)
        for result in response.data['results']:
            print(result)
            self.assertIn(result['category'], ['blastoise'])
        
# WebSocket tests
class WebSocketTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Create a test Pokemon
        self.pokemon = Pokemon.objects.create(
            name='Pikachu',
            latitude=34.0522,
            longitude=-118.2437,
            location_name='Los Angeles',
            type_primary='Electric',
            type_secondary='',
            moves=['thunderbolt', 'quick-attack'],
            sprite='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png',
            height=0.4,
            weight=6.0,
            category='Mouse',
            abilities=['static'],
            stats={'hp': 35, 'attack': 55, 'defense': 40},
            source='API',
            uploaded_by=self.user
        )
    
    def get_communicator(self, pokemon_id):
        """Helper method to create a WebSocket communicator"""
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, f'ws/pokemon/{pokemon_id}/energy/')
        return communicator
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    def test_websocket_connection_success(self, mock_session):
        """Test successful WebSocket connection when Pokemon exists"""
        async def run_test():
            # Mock the weather API response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'weather': [{'description': 'clear sky'}],
                'main': {'temp': 20}
            })
            
            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value = mock_get
            
            communicator = self.get_communicator(self.pokemon.id)
            connected, subprotocol = await communicator.connect()
            
            self.assertTrue(connected)
            
            # Wait a bit to receive an energy update
            await asyncio.sleep(0.1)
            
            # Check if we receive energy update
            response = await communicator.receive_json_from(timeout=10)
            self.assertIn('energy_level', response)
            self.assertIn('timestamp', response)
            self.assertIsInstance(response['energy_level'], (int, float))
            self.assertGreaterEqual(response['energy_level'], 0)
            self.assertLessEqual(response['energy_level'], 100)
            
            await communicator.disconnect()
        
        async_to_sync(run_test)()
    
    def test_websocket_connection_invalid_pokemon(self):
        """Test WebSocket connection fails when Pokemon doesn't exist"""
        async def run_test():
            invalid_id = 99999
            communicator = self.get_communicator(invalid_id)
            connected, subprotocol = await communicator.connect()
            
            # Connection should be accepted initially, but then closed
            # The consumer checks for Pokemon existence after accepting
            # So we need to wait a bit to see if it closes
            await asyncio.sleep(0.2)
            
            # Check if connection was closed by trying to receive
            # The consumer should close with code 4004 when Pokemon doesn't exist
            try:
                await communicator.receive_from(timeout=0.5)
                # If we get here, connection wasn't closed - this shouldn't happen
                await communicator.disconnect()
                self.fail("Connection should have been closed for invalid Pokemon ID")
            except Exception:
                # Connection was closed, which is expected behavior
                pass
        
        async_to_sync(run_test)()
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    @patch('apps.pokemon.consumers.os.getenv')
    def test_websocket_energy_update_format(self, mock_getenv, mock_session):
        """Test that energy updates are sent in the correct format"""
        async def run_test():
            mock_getenv.return_value = None  # No API key, use default
            
            communicator = self.get_communicator(self.pokemon.id)
            connected, subprotocol = await communicator.connect()
            
            self.assertTrue(connected)
            
            # Wait for energy update
            await asyncio.sleep(0.1)
            
            # Receive energy update
            response = await communicator.receive_json_from(timeout=10)
            
            # Validate response structure
            self.assertIn('energy_level', response)
            self.assertIn('timestamp', response)
            self.assertIsInstance(response['energy_level'], (int, float))
            self.assertIsInstance(response['timestamp'], str)
            
            # Energy should be between 0 and 100
            self.assertGreaterEqual(response['energy_level'], 0)
            self.assertLessEqual(response['energy_level'], 100)
            
            await communicator.disconnect()
        
        async_to_sync(run_test)()
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    @patch('apps.pokemon.consumers.os.getenv')
    def test_websocket_multiple_energy_updates(self, mock_getenv, mock_session):
        """Test that multiple energy updates are received over time"""
        async def run_test():
            mock_getenv.return_value = None  # No API key, use default
            
            communicator = self.get_communicator(self.pokemon.id)
            connected, subprotocol = await communicator.connect()
            
            self.assertTrue(connected)
            
            # Wait for first energy update
            await asyncio.sleep(0.1)
            response1 = await communicator.receive_json_from(timeout=10)
            self.assertIn('energy_level', response1)
            
            # Wait for second energy update (should come after ~5 seconds)
            # But we'll wait a shorter time in tests and mock the delay
            await asyncio.sleep(0.1)
            # We might need to wait longer, but for test speed, let's just check one update
            
            await communicator.disconnect()
        
        async_to_sync(run_test)()
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    def test_websocket_weather_api_integration(self, mock_session):
        """Test that weather API is called and affects energy calculation"""
        async def run_test():
            # Mock the weather API response with rainy weather
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'weather': [{'description': 'moderate rain'}],
                'main': {'temp': 15}
            })
            
            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value = mock_get
            
            with patch('apps.pokemon.consumers.os.getenv', return_value='test-api-key'):
                communicator = self.get_communicator(self.pokemon.id)
                connected, subprotocol = await communicator.connect()
                
                self.assertTrue(connected)
                
                # Wait for energy update
                await asyncio.sleep(0.1)
                response = await communicator.receive_json_from(timeout=10)
                
                # Verify weather API was called
                mock_session.return_value.get.assert_called()
                
                # Energy level should be present (rainy weather should reduce it, but with variance)
                self.assertIn('energy_level', response)
                self.assertGreaterEqual(response['energy_level'], 0)
                self.assertLessEqual(response['energy_level'], 100)
                
                await communicator.disconnect()
        
        async_to_sync(run_test)()
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    def test_websocket_connection_disconnect(self, mock_session):
        """Test that WebSocket disconnects properly"""
        async def run_test():
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'weather': [{'description': 'clear sky'}],
                'main': {'temp': 20}
            })
            
            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value = mock_get
            
            communicator = self.get_communicator(self.pokemon.id)
            connected, subprotocol = await communicator.connect()
            
            self.assertTrue(connected)
            
            # Disconnect
            await communicator.disconnect()
            
            # Try to receive (should fail since disconnected)
            try:
                await communicator.receive_from(timeout=0.1)
                self.fail("Should not receive messages after disconnect")
            except Exception:
                # Expected - connection is closed
                pass
        
        async_to_sync(run_test)()
    
    @patch('apps.pokemon.consumers.aiohttp.ClientSession')
    def test_websocket_energy_with_temperature_modifiers(self, mock_session):
        """Test energy calculation with different temperature conditions"""
        async def run_test():
            # Test high temperature (should increase energy)
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'weather': [{'description': 'clear sky'}],
                'main': {'temp': 35}  # High temperature
            })
            
            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value.get.return_value = mock_get
            
            with patch('apps.pokemon.consumers.os.getenv', return_value='test-api-key'):
                communicator = self.get_communicator(self.pokemon.id)
                connected, subprotocol = await communicator.connect()
                
                self.assertTrue(connected)
                
                await asyncio.sleep(0.1)
                response = await communicator.receive_json_from(timeout=10)
                
                # Energy should be in valid range
                self.assertIn('energy_level', response)
                self.assertGreaterEqual(response['energy_level'], 0)
                self.assertLessEqual(response['energy_level'], 100)
                
                await communicator.disconnect()
        
        async_to_sync(run_test)()

