# apps/pokemon/models.py

from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(max_length=255)
    
    # Location
    latitude = models.FloatField() # latitude of the pokemon's location
    longitude = models.FloatField() # longitude of the pokemon's location
    location_name = models.CharField(max_length=255, blank=True) # name of the location where the pokemon was found
    
    # Type
    type_primary = models.CharField(max_length=50)
    
    # Moves
    moves = models.JSONField(default=list) # list of the latest moves the pokemon has learned
    
    # Sprite
    sprite = models.URLField() # URL of the sprite of the pokemon

    # Optional Fields?    
    height = models.FloatField(null=True, blank=True) # height of the pokemon in meters
    weight = models.FloatField(null=True, blank=True) # weight of the pokemon in kilograms
    category = models.CharField(max_length=255, blank=True) # category of the pokemon
    abilities = models.JSONField(default=list, blank=True) # list of the abilities the pokemon has
    
    # Types
    type_secondary = models.CharField(max_length=50, blank=True)
    
    # Stats
    stats = models.JSONField(default=dict, blank=True) # dictionary of the stats of the pokemon
    
    # source tracking
    source = models.CharField(max_length=20, choices = [
        ('API', 'PokeAPI'),
        ('CSV', 'User Upload')
    ])
    
    # user relation
    uploaded_by = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        null = True,
        blank = True,
        related_name = 'uploaded_pokemon'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class FavoritePokemon(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    pokemon = models.ForeignKey(Pokemon, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'pokemon')