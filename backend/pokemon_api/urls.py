# pokemon_api/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.pokemon.views import PokemonViewSet
from apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r'pokemon', PokemonViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]