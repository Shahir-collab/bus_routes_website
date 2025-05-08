import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { GoogleMap, Marker, Polyline } from '@react-google-maps/api';
import BusInfo from '../../components/BusInfo';

const BusDetails = () => {
  const { id } = useParams();
  const [bus, setBus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentLocation, setCurrentLocation] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  
  useEffect(() => {
    const fetchBusDetails = async () => {
      try {
        const response = await axios.get(`/api/buses/${id}/`);
        setBus(response.data);
        
        // Get route points for the map
        const routeResponse = await axios.get(`/api/routes/${response.data.routeId}/`);
        setRoutePoints(routeResponse.data.points);
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch bus details.');
        setLoading(false);
      }
    };
    
    fetchBusDetails();
    
    // Set up real-time tracking
    const locationTracker = setInterval(async () => {
      try {
        const locationResponse = await axios.get(`/api/buses/${id}/location/`);
        setCurrentLocation(locationResponse.data);
      } catch (err) {
        console.error('Error fetching location:', err);
      }
    }, 10000); // Update every 10 seconds
    
    return () => clearInterval(locationTracker);
  }, [id]);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger mt-5" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="bus-details-container">
      <h2>Bus Details</h2>
      
      {bus && (
        <>
          <BusInfo bus={bus} />
          
          <div className="map-container mt-4">
            <h4>Real-Time Tracking</h4>
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '400px' }}
              center={currentLocation || routePoints[0]}
              zoom={12}
            >
              {/* Bus current position marker */}
              {currentLocation && (
                <Marker
                  position={currentLocation}
                  icon={{
                    url: '/bus-icon.png',
                    scaledSize: new window.google.maps.Size(40, 40)
                  }}
                />
              )}
              
              {/* Route line */}
              <Polyline
                path={routePoints}
                options={{
                  strokeColor: '#0088FF',
                  strokeWeight: 3,
                  strokeOpacity: 0.8
                }}
              />
              
              {/* Station markers */}
              {bus.stations.map((station, index) => (
                <Marker
                  key={index}
                  position={{ lat: station.latitude, lng: station.longitude }}
                  icon={{
                    url: '/station-icon.png',
                    scaledSize: new window.google.maps.Size(20, 20)
                  }}
                />
              ))}
            </GoogleMap>
          </div>
          
          <div className="schedule-container mt-4">
            <h4>Route Schedule</h4>
            <table className="table">
              <thead>
                <tr>
                  <th>Station</th>
                  <th>Arrival Time</th>
                  <th>Departure Time</th>
                </tr>
              </thead>
              <tbody>
                {bus.stations.map((station, index) => (
                  <tr key={index}>
                    <td>{station.name}</td>
                    <td>{station.arrivalTime || 'Start'}</td>
                    <td>{station.departureTime || 'End'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default BusDetails;