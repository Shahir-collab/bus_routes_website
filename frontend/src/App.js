import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { AuthProvider } from './utils/AuthContext';
import PrivateRoute from './utils/PrivateRoute';

// User Portal Pages
import Home from './pages/user/Home';
import Login from './pages/user/Login';
import Register from './pages/user/Register';
import BusSearch from './pages/user/BusSearch';
import BusDetails from './pages/user/BusDetails';
import UserProfile from './pages/user/UserProfile';

// Admin Portal Pages
import AdminLogin from './pages/admin/AdminLogin';
import AdminDashboard from './pages/admin/AdminDashboard';
import BusManagement from './pages/admin/BusManagement';
import StationManagement from './pages/admin/StationManagement';
import ScheduleManagement from './pages/admin/ScheduleManagement';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <div className="container">
          <Switch>
            {/* Public Routes */}
            <Route exact path="/" component={Home} />
            <Route path="/login" component={Login} />
            <Route path="/register" component={Register} />
            
            {/* User Routes */}
            <PrivateRoute path="/search" component={BusSearch} />
            <PrivateRoute path="/bus/:id" component={BusDetails} />
            <PrivateRoute path="/profile" component={UserProfile} />
            
            {/* Admin Routes */}
            <Route path="/admin/login" component={AdminLogin} />
            <PrivateRoute path="/admin/dashboard" component={AdminDashboard} adminRoute={true} />
            <PrivateRoute path="/admin/buses" component={BusManagement} adminRoute={true} />
            <PrivateRoute path="/admin/stations" component={StationManagement} adminRoute={true} />
            <PrivateRoute path="/admin/schedules" component={ScheduleManagement} adminRoute={true} />
          </Switch>
        </div>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;