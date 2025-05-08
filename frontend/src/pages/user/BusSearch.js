import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import axios from 'axios';
import BusSearchForm from '../../components/BusSearchForm';
import BusList from '../../components/BusList';

const BusSearch = () => {
  const [stations, setStations] = useState([]);
  const [buses, setBuses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useState({
    startStation: '',
    endStation: '',
    time: ''
  });
  const [filters, setFilters] = useState({
    busType: 'all',
    departureTime: ''
  });
  
  const history = useHistory();

  useEffect(() => {
    // Fetch all stations
    const fetchStations = async () => {
      try {
        const response = await axios.get('/api/stations/');
        setStations(response.data);
      } catch (error) {
        console.error('Error fetching stations:', error);
      }
    };

    fetchStations();
  }, []);

  const handleSearch = async (params) => {
    setLoading(true);
    setSearchParams(params);
    
    try {
      const response = await axios.get('/api/buses/search/', { params });
      setBuses(response.data);
    } catch (error) {
      console.error('Error searching buses:', error);
    }
    
    setLoading(false);
  };

  const handleFilter = (newFilters) => {
    setFilters(newFilters);
    
    // Apply filters to the current bus list
    // This is a client-side filter since we already have the bus data
  };

  const handleBusSelect = (busId) => {
    history.push(`/bus/${busId}`);
  };

  // Filter buses based on current filters
  const filteredBuses = buses.filter(bus => {
    if (filters.busType !== 'all' && bus.type !== filters.busType) {
      return false;
    }
    
    if (filters.departureTime && new Date(bus.departureTime) < new Date(filters.departureTime)) {
      return false;
    }
    
    return true;
  });

  return (
    <div className="bus-search-container">
      <h2>Find Your Bus</h2>
      
      <BusSearchForm 
        stations={stations} 
        onSearch={handleSearch} 
      />
      
      {loading ? (
        <div className="text-center mt-4">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      ) : (
        <>
          {buses.length > 0 && (
            <div className="filter-container mt-4">
              <h4>Filter Results</h4>
              <div className="row">
                <div className="col-md-6">
                  <label>Bus Type</label>
                  <select 
                    className="form-control"
                    value={filters.busType}
                    onChange={(e) => setFilters({...filters, busType: e.target.value})}
                  >
                    <option value="all">All Types</option>
                    <option value="regular">Regular</option>
                    <option value="fast">Fast</option>
                    <option value="superfast">Superfast</option>
                  </select>
                </div>
                <div className="col-md-6">
                  <label>Minimum Departure Time</label>
                  <input 
                    type="time" 
                    className="form-control"
                    value={filters.departureTime}
                    onChange={(e) => setFilters({...filters, departureTime: e.target.value})}
                  />
                </div>
              </div>
            </div>
          )}
          
          <BusList 
            buses={filteredBuses} 
            onBusSelect={handleBusSelect} 
          />
        </>
      )}
    </div>
  );
};

export default BusSearch;