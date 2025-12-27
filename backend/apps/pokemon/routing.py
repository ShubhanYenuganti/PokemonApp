# apps/pokemon/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pokemon/(?P<pokemon_id>\d+)/energy/$', consumers.PokemonEnergyConsumer.as_asgi()),
]

