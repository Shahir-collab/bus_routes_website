import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import DashboardStats from '../../components/admin/DashboardStats';
import BusStatusList from '../../components/admin/BusStatusList';
import RecentAlerts from '../../components/admin/RecentAlerts';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalBuses: 0,
    activeBuses: 0,
    totalStations: 0,
    totalRoutes: 0
  });
  const [busStatus, setBusStatus] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch dashboard summary stats
        const statsResponse = await axios.get('/api/admin/dashboard/stats/');
        setStats(statsResponse.data);
        
        // Fetch active bus status
        const busStatusResponse = await axios.get('/api/admin/buses/status/');
        setBusStatus(busStatusResponse.data);
        
        // Fetch recent alerts
        const alertsResponse = await axios.get('/api/admin/alerts/');
        setAlerts(alertsResponse.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Set up real-time updates for bus status
    const statusUpdater = setInterval(async () => {
      try {
        const response = await axios.get('/api/admin/buses/status/');
        setBusStatus(response.data);
      } catch (err) {
        console.error('Error updating bus status:', err);
      }
    }, 30000); // Update every 30 seconds
    
    return () => clearInterval(statusUpdater);
  }, []);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-container">
      <h2>Admin Dashboard</h2>
      
      <div className="quick-actions mb-4">
        <div className="row">
          <div className="col-md-3">
            <Link to="/admin/buses" className="btn btn-primary btn-block">
              Manage Buses
            </Link>
          </div>
          <div className="col-md-3">
            <Link to="/admin/stations" className="btn btn-success btn-block">
              Manage Stations
            </Link>
          </div>
          <div className="col-md-3">
            <Link to="/admin/schedules" className="btn btn-info btn-block">
              Manage Schedules
            </Link>
          </div>
          <div className="col-md-3">
            <Link to="/admin/reports" className="btn btn-secondary btn-block">
              View Reports
            </Link>
          </div>
        </div>
      </div>
      
      <DashboardStats stats={stats} />
      
      <div className="row mt-4">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h5>Active Bus Status</h5>
            </div>
            <div className="card-body">
              <BusStatusList buses={busStatus} />
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5>Recent Alerts</h5>
            </div>
            <div className="card-body">
              <RecentAlerts alerts={alerts} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;