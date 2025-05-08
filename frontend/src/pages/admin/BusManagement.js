import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BusForm from '../../components/admin/BusForm';
import BusTable from '../../components/admin/BusTable';

const BusManagement = () => {
  const [buses, setBuses] = useState([]);
  const [selectedBus, setSelectedBus] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBuses();
  }, []);

  const fetchBuses = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/admin/buses/');
      setBuses(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch buses.');
      setLoading(false);
    }
  };

  const handleAddBus = () => {
    setSelectedBus(null);
    setIsEditing(true);
  };

  const handleEditBus = (bus) => {
    setSelectedBus(bus);
    setIsEditing(true);
  };

  const handleDeleteBus = async (busId) => {
    if (window.confirm('Are you sure you want to delete this bus?')) {
      try {
        await axios.delete(`/api/admin/buses/${busId}/`);
        setBuses(buses.filter(bus => bus.id !== busId));
      } catch (err) {
        setError('Failed to delete bus.');
      }
    }
  };

  const handleSubmit = async (busData) => {
    try {
      if (selectedBus) {
        // Update existing bus
        await axios.put(`/api/admin/buses/${selectedBus.id}/`, busData);
      } else {
        // Create new bus
        await axios.post('/api/admin/buses/', busData);
      }
      
      fetchBuses();
      setIsEditing(false);
    } catch (err) {
      setError('Failed to save bus data.');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <div className="bus-management-container">
      <h2>Bus Management</h2>
      
      {error && <div className="alert alert-danger">{error}</div>}
      
      {isEditing ? (
        <div className="card">
          <div className="card-header">
            <h5>{selectedBus ? 'Edit Bus' : 'Add New Bus'}</h5>
          </div>
          <div className="card-body">
            <BusForm 
              bus={selectedBus} 
              onSubmit={handleSubmit} 
              onCancel={handleCancel} 
            />
          </div>
        </div>
      ) : (
        <>
          <div className="mb-3">
            <button 
              className="btn btn-primary" 
              onClick={handleAddBus}
            >
              Add New Bus
            </button>
          </div>
          
          {loading ? (
            <div className="text-center">
              <div className="spinner-border" role="status">
                <span className="sr-only">Loading...</span>
              </div>
            </div>
          ) : (
            <BusTable 
              buses={buses} 
              onEdit={handleEditBus} 
              onDelete={handleDeleteBus} 
            />
          )}
        </>
      )}
    </div>
  );
};

export default BusManagement;