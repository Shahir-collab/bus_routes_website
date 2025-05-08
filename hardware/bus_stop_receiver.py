import time
import json
import serial
import requests
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Configuration
STATION_ID = "1"  # This would be configured per station
API_URL = "http://your-server.com/api/station/update/"
API_KEY = "your-api-key"

# Firebase setup
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-app.firebaseio.com'
})

# Serial connection to the transceiver
try:
    transceiver = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    print("Transceiver connected successfully")
except Exception as e:
    print(f"Error connecting to transceiver: {e}")
    exit(1)

def update_display(bus_data):
    """
    Update the station's display with information about approaching buses
    In a real implementation, this would communicate with an actual display
    """
    print("\n--- STATION DISPLAY UPDATE ---")
    print(f"Station ID: {STATION_ID}")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    print("\nApproaching buses:")
    
    for bus in bus_data:
        print(f"Bus {bus['bus_id']} - ETA: {bus['eta']} minutes")
    
    print("-----------------------------\n")

def notify_server(bus_data):
    """
    Notify the server about bus arrivals
    """
    try:
        headers = {
            'Authorization': f'Token {API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'station_id': STATION_ID,
            'bus_data': bus_data
        }
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            print("Server updated successfully")
        else:
            print(f"Server error: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to server: {e}")

def update_firebase(bus_data):
    """
    Update Firebase with real-time bus information
    """
    try:
        ref = db.reference(f'station_updates/{STATION_ID}')
        ref.set({
            'timestamp': time.time(),
            'buses': bus_data
        })
        print("Firebase updated successfully")
    except Exception as e:
        print(f"Firebase error: {e}")

def main():
    print(f"Bus stop receiver starting for Station {STATION_ID}...")
    
    # Keep track of buses we've seen recently
    recent_buses = {}
    
    while True:
        try:
            # Check for incoming signals from buses
            if transceiver.in_waiting > 0:
                data = transceiver.readline().decode('utf-8').strip()
                try:
                    bus_info = json.loads(data)
                    bus_id = bus_info['bus_id']
                    eta = bus_info['eta']
                    
                    # Store the bus info with timestamp
                    recent_buses[bus_id] = {
                        'bus_id': bus_id,
                        'eta': eta,
                        'last_seen': time.time()
                    }
                    
                    print(f"Received signal from Bus {bus_id}, ETA: {eta} minutes")
                except json.JSONDecodeError:
                    print(f"Received invalid data: {data}")
            
            # Clean up old bus data (older than 5 minutes)
            current_time = time.time()
            buses_to_remove = []
            for bus_id, info in recent_buses.items():
                if current_time - info['last_seen'] > 300:  # 5 minutes
                    buses_to_remove.append(bus_id)
            
            for bus_id in buses_to_remove:
                del recent_buses[bus_id]
            
            # Update displays and server if we have bus data
            if recent_buses:
                bus_data = list(recent_buses.values())
                update_display(bus_data)
                notify_server(bus_data)
                update_firebase(bus_data)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait a bit longer if there's an error

if __name__ == "__main__":
    main()