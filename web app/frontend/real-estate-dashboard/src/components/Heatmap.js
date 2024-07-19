import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, HeatmapLayer } from '@react-google-maps/api';
import axios from 'axios';

const containerStyle = {
    width: '80%',
    height: '80vh',
  };

const center = {
  lat: -20.2,
  lng: 57.5,
};

// Keep the libraries array as a static variable
const libraries = ['visualization'];

const Heatmap = () => {
  const [heatmapData, setHeatmapData] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/locations/')
      .then(response => {
        const data = response.data.map(location => {
          const lat = parseFloat(location.latitude);
          const lng = parseFloat(location.longitude);
          const avgPrice = parseFloat(location.average_price);
          if (!isNaN(lat) && !isNaN(lng) && !isNaN(avgPrice)) {
            return { location: new window.google.maps.LatLng(lat, lng), weight: avgPrice };
          }
          return null;
        }).filter(Boolean); // Remove any null values
        setHeatmapData(data);
        console.log("Heatmap data:", data); // Log the data to verify it
      })
      .catch(error => console.error('Error fetching locations:', error));
  }, []);

  const heatmapOptions = {
    radius: 50, // Increase the radius to make heat points bigger
    opacity: 0.6, // Adjust opacity to make the heatmap more or less transparent
    dissipating: true, // Controls whether the radius of influence is relative to the map's zoom level
  };

  return (
    <LoadScript
      googleMapsApiKey="AIzaSyBu3sgFLYHYqrwUgGY7UHBbu-XW9WzjFj8"
      libraries={libraries}  // Use the static variable here
    >
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={10}
      >
        <HeatmapLayer data={heatmapData.map(point => ({ location: point.location, weight: point.weight }))} options={heatmapOptions} />
      </GoogleMap>
    </LoadScript>
  );
};

export default Heatmap;
