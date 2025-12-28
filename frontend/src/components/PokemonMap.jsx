import React, { useState, useRef, useImperativeHandle, forwardRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const MAP_LAYERS = {
  street: {
    name: 'Street Map',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors'
  },
  satellite: {
    name: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri'
  },
  topographic: {
    name: 'Topographic',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors'
  },
  terrain: {
    name: 'Terrain',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri'
  },
};

// Component to access map instance
const MapController = forwardRef(({ targetPosition }, ref) => {
  const map = useMap();
  
  useImperativeHandle(ref, () => ({
    flyTo: (lat, lng, zoom = 16) => {
      map.flyTo([lat, lng], zoom, {
        duration: 1.5
      });
    }
  }));
  
  return null;
});

const PokemonMap = forwardRef(({ pokemonList = [], onPokemonClick }, ref) => {
  // Los Angeles, CA coordinates
  const losAngelesCenter = [34.0522, -118.2437];
  const [selectedLayer, setSelectedLayer] = useState('street');
  const mapControllerRef = useRef();
  
  useImperativeHandle(ref, () => ({
    flyToPokemon: (pokemon) => {
      if (pokemon && pokemon.latitude && pokemon.longitude && mapControllerRef.current) {
        mapControllerRef.current.flyTo(pokemon.latitude, pokemon.longitude);
      }
    }
  }));

  // Create a custom icon from Pokemon sprite
  const createPokemonIcon = (spriteUrl) => {
    return L.icon({
      iconUrl: spriteUrl,
      iconSize: [40, 40],
      iconAnchor: [20, 40],
      popupAnchor: [0, -40],
      className: 'pokemon-icon'
    });
  }
  
  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      {/* Layer Selector */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 1000,
        backgroundColor: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
      }}>
        <label htmlFor="layer-select" style={{ marginRight: '8px', fontWeight: 'bold' }}>
          Map Layer:
        </label>
        <select
          id="layer-select"
          value={selectedLayer}
          onChange={(e) => setSelectedLayer(e.target.value)}
          style={{
            padding: '4px 8px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            cursor: 'pointer'
          }}
        >
          {Object.entries(MAP_LAYERS).map(([key, layer]) => (
            <option key={key} value={key}>
              {layer.name}
            </option>
          ))}
        </select>
      </div>

      <MapContainer 
        center={losAngelesCenter} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <MapController ref={mapControllerRef} />
        <TileLayer
          key={selectedLayer}
          attribution={MAP_LAYERS[selectedLayer].attribution}
          url={MAP_LAYERS[selectedLayer].url}
        />
        {/* Render Pokemon markers */}
        {pokemonList.filter(
          pokemon => pokemon.latitude && pokemon.longitude && pokemon.sprite)
          .map(pokemon => (
            <Marker
              key={pokemon.id}
              position={[pokemon.latitude, pokemon.longitude]}
              icon={createPokemonIcon(pokemon.sprite)}
              eventHandlers={{
                click: () => {
                  if (onPokemonClick) {
                    onPokemonClick(pokemon);
                  }
                }
              }}
            >
              <Popup>
                <div style={{ textAlign: 'center' }}>
                  <img 
                    src={pokemon.sprite} 
                    alt={pokemon.name} 
                    style={{ width: '60px', height: '60px' }}
                  />
                  <div style={{ fontWeight: 'bold', marginTop: '5px' }}>
                    {pokemon.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {pokemon.type_primary}
                    {pokemon.type_secondary && ` / ${pokemon.type_secondary}`}
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        )}
      </MapContainer>

      {/* Add custom CSS for marker icons */}
      <style jsx>{`
        .pokemon-marker-icon {
          background: white;
          border-radius: 50%;
          border: 2px solid #333;
          box-shadow: 0 2px 5px rgba(0,0,0,0.3);
          cursor: pointer;
          transition: transform 0.2s;
        }
        .pokemon-marker-icon:hover {
          transform: scale(1.1);
          z-index: 1000 !important;
        }
      `}</style>

    </div>
  );
});

export default PokemonMap;