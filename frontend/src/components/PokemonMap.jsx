import React, { useState } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

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

const PokemonMap = () => {
  // Los Angeles, CA coordinates
  const losAngelesCenter = [34.0522, -118.2437];
  const [selectedLayer, setSelectedLayer] = useState('street');
  
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
        <TileLayer
          key={selectedLayer}
          attribution={MAP_LAYERS[selectedLayer].attribution}
          url={MAP_LAYERS[selectedLayer].url}
        />
      </MapContainer>
    </div>
  );
};

export default PokemonMap;