import time
import json
import random
import requests
import serial
import firebase_admin
from firebase_admin import credentials, db
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

# Configuration
API_URL = "http://your-server.com/api/bus/location/update/"
API_KEY = "your-api-key"
BUS_ID = "1"  # This would be configured per bus

# Firebase setup
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-app.firebaseio.com'
})

# GPS setup
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

# Serial connection to the transceiver
try:
    transceiver = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    transceiver_connected = True
except:
    print("Warning: Transceiver not connected")
    transceiver_connected = False

def get_gps_data():
    try:
        gpsd.next()
        if gpsd.fix.mode > 1:  # If we have a fix
            return {
                'latitude': gpsd.fix.latitude,
                'longitude': gpsd.fix.longitude,
                'speed': gpsd.fix.speed,
                'heading': gpsd.fix.track,
                'timestamp': time.time()
            }
        else:
            print("No GPS fix")
            return None
    except Exception as e:
        print(f"GPS error: {e}")
        # In case of GPS failure, return a simulated location for testing
        return {
            'latitude': 37.7749 + random.uniform(-0.01, 0.01),
            'longitude': -122.4194 + random.uniform(-0.01, 0.01),
            'speed': random.uniform(0, 60),
            'heading': random.uniform(0, 359),
            'timestamp': time.time()
        }

def send_location_to_server(location_data):
    try:
        headers = {
            'Authorization': f'Token {API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'bus_id': BUS_ID,
            **location_data
        }
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            print("Location updated successfully")
        else:
            print(f"Server error: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to server: {e}")

def update_firebase_location(location_data):
    try:
        ref = db.reference(f'bus_locations/{BUS_ID}')
        ref.set(location_data)
        print("Firebase updated successfully")
    except Exception as e:
        print(f"Firebase error: {e}")

def check_nearby_stations(location_data):
    if not transceiver_connected:
        return
    
    try:
        # This would be a more complex algorithm in a real implementation
        # Here we're just simulating the process
        
        # Get list of nearby stations from the server
        headers = {
            'Authorization': f'Token {API_KEY}',
            'Content-Type': 'application/json'
        }
        params = {
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'radius': 0.5  # km
        }
        response = requests.get(
            "http://your-server.com/api/stations/nearby/",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            nearby_stations = response.json()
            
            for station in nearby_stations:
                # Send signal to the station via transceiver
                message = json.dumps({
                    'bus_id': BUS_ID,
                    'station_id': station['id'],
                    'eta': station['eta']  # Estimated Time of Arrival
                })
                transceiver.write(message.encode())
                print(f"Sent signal to station {station['id']}")
        
    except Exception as e:
        print(f"Error checking nearby stations: {e}")

def main():
    print("Bus GPS tracker starting...")
    
    while True:
        location_data = get_gps_data()
        
        if location_data:
            # Update server
            send_location_to_server(location_data)
            
            # Update Firebase for real-time tracking
            update_firebase_location(location_data)
            
            # Check for nearby stations
            check_nearby_stations(location_data)
        
        # Wait before next update
        time.sleep(5)

if __name__ == "__main__":
    main()