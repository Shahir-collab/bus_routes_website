from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Station, Route, RoutePoint, Bus, Schedule, 
    StationSchedule, BusLocation, Alert, Booking
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ['id', 'latitude', 'longitude', 'order']

class RouteSerializer(serializers.ModelSerializer):
    points = RoutePointSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'points', 'created_at', 'updated_at']

class BusLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLocation
        fields = ['latitude', 'longitude', 'speed', 'heading', 'timestamp']

class BusSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.name', read_only=True)
    current_location = BusLocationSerializer(source='location', read_only=True)
    
    class Meta:
        model = Bus
        fields = ['id', 'number', 'type', 'capacity', 'route', 'route_name', 
                  'is_active', 'current_location', 'created_at', 'updated_at']

class StationScheduleSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = StationSchedule
        fields = ['id', 'station', 'station_name', 'arrival_time', 'departure_time', 'order']

class ScheduleSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.number', read_only=True)
    bus_type = serializers.CharField(source='bus.type', read_only=True)
    start_station_name = serializers.CharField(source='start_station.name', read_only=True)
    end_station_name = serializers.CharField(source='end_station.name', read_only=True)
    station_schedules = StationScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'bus', 'bus_number', 'bus_type', 'start_station', 'start_station_name',
                  'end_station', 'end_station_name', 'departure_time', 'arrival_time',
                  'is_active', 'station_schedules', 'created_at', 'updated_at']

class AlertSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.number', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'bus', 'bus_number', 'station', 'station_name', 
                  'alert_type', 'message', 'is_resolved', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    bus_number = serializers.CharField(source='schedule.bus.number', read_only=True)
    boarding_station_name = serializers.CharField(source='boarding_station.name', read_only=True)
    destination_station_name = serializers.CharField(source='destination_station.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'username', 'schedule', 'bus_number',
                  'boarding_station', 'boarding_station_name',
                  'destination_station', 'destination_station_name',
                  'booking_time', 'status']