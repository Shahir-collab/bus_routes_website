from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    Station, Route, RoutePoint, Bus, Schedule, 
    StationSchedule, BusLocation, Alert, Booking
)
from .serializers import (
    UserSerializer, StationSerializer, RouteSerializer, 
    BusSerializer, ScheduleSerializer, BusLocationSerializer,
    AlertSerializer, BookingSerializer
)

# User API views
class StationListView(generics.ListAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_buses(request):
    start_station_id = request.query_params.get('startStation')
    end_station_id = request.query_params.get('endStation')
    time_str = request.query_params.get('time')
    
    if not all([start_station_id, end_station_id, time_str]):
        return Response(
            {"error": "Start station, end station, and time are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Parse the time
    try:
        search_time = timezone.datetime.strptime(time_str, '%H:%M').time()
        today = timezone.now().date()
        search_datetime = timezone.make_aware(timezone.datetime.combine(today, search_time))
    except ValueError:
        return Response(
            {"error": "Invalid time format. Use HH:MM"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find schedules that match the criteria
    schedules = Schedule.objects.filter(
        start_station_id=start_station_id,
        end_station_id=end_station_id,
        departure_time__gte=search_datetime,
        is_active=True
    ).select_related('bus', 'start_station', 'end_station')
    
    # Prepare the response data
    data = []
    for schedule in schedules:
        # Get the bus location if available
        try:
            location = BusLocation.objects.get(bus=schedule.bus)
            location_data = {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
        except BusLocation.DoesNotExist:
            location_data = None
        
        # Get all stops for this schedule
        stops = StationSchedule.objects.filter(
            schedule=schedule
        ).select_related('station').order_by('order')
        
        stops_data = []
        for stop in stops:
            stops_data.append({
                'id': stop.station.id,
                'name': stop.station.name,
                'arrival_time': stop.arrival_time,
                'departure_time': stop.departure_time
            })
        
        data.append({
            'id': schedule.id,
            'bus_number': schedule.bus.number,
            'bus_type': schedule.bus.type,
            'departure_time': schedule.departure_time,
            'arrival_time': schedule.arrival_time,
            'start_station': schedule.start_station.name,
            'end_station': schedule.end_station.name,
            'current_location': location_data,
            'stops': stops_data
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_bus_details(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    
    # Get active schedules for this bus
    schedules = Schedule.objects.filter(
        bus=bus,
        is_active=True,
        departure_time__gte=timezone.now()
    ).select_related('start_station', 'end_station').order_by('departure_time')
    
    # Get the current location
    try:
        location = BusLocation.objects.get(bus=bus)
        location_data = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location_data.timestamp
        }
    except BusLocation.DoesNotExist:
        location_data = None
    
    # Get the route points
    route_points = []
    if bus.route:
        points = RoutePoint.objects.filter(route=bus.route).order_by('order')
        route_points = [{'latitude': p.latitude, 'longitude': p.longitude} for p in points]
    
    # Prepare schedule data
    schedule_data = []
    for schedule in schedules:
        stops = StationSchedule.objects.filter(
            schedule=schedule
        ).select_related('station').order_by('order')
        
        stops_data = []
        for stop in stops:
            stops_data.append({
                'id': stop.station.id,
                'name': stop.station.name,
                'arrival_time': stop.arrival_time,
                'departure_time': stop.departure_time
            })
        
        schedule_data.append({
            'id': schedule.id,
            'departure_time': schedule.departure_time,
            'arrival_time': schedule.arrival_time,
            'start_station': schedule.start_station.name,
            'end_station': schedule.end_station.name,
            'stops': stops_data
        })
    
    data = {
        'id': bus.id,
        'number': bus.number,
        'type': bus.type,
        'capacity': bus.capacity,
        'is_active': bus.is_active,
        'current_location': location_data,
        'route_points': route_points,
        'schedules': schedule_data
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_bus_location(request, bus_id):
    try:
        location = BusLocation.objects.get(bus_id=bus_id)
        return Response({
            'latitude': location.latitude,
            'longitude': location.longitude,
            'speed': location.speed,
            'heading': location.heading,
            'timestamp': location.timestamp
        })
    except BusLocation.DoesNotExist:
        return Response(
            {"error": "Location not available for this bus"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_booking(request):
    user = request.user
    schedule_id = request.data.get('schedule')
    boarding_station_id = request.data.get('boarding_station')
    destination_station_id = request.data.get('destination_station')
    
    if not all([schedule_id, boarding_station_id, destination_station_id]):
        return Response(
            {"error": "Schedule, boarding station, and destination station are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        schedule = Schedule.objects.get(id=schedule_id, is_active=True)
        boarding_station = Station.objects.get(id=boarding_station_id)
        destination_station = Station.objects.get(id=destination_station_id)
        
        # Check if the stations are on the schedule's route
        boarding_in_schedule = StationSchedule.objects.filter(
            schedule=schedule, station=boarding_station
        ).exists()
        
        destination_in_schedule = StationSchedule.objects.filter(
            schedule=schedule, station=destination_station
        ).exists()
        
        if not (boarding_in_schedule and destination_in_schedule):
            return Response(
                {"error": "Selected stations are not on this bus route"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the booking
        booking = Booking.objects.create(
            user=user,
            schedule=schedule,
            boarding_station=boarding_station,
            destination_station=destination_station,
            status='confirmed'
        )
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Schedule.DoesNotExist:
        return Response(
            {"error": "Invalid schedule"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Station.DoesNotExist:
        return Response(
            {"error": "Invalid station"},
            status=status.HTTP_400_BAD_REQUEST
        )

# Admin API views
class AdminBusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminStationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminRouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminAlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard_stats(request):
    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(is_active=True).count()
    total_stations = Station.objects.count()
    total_routes = Route.objects.count()
    
    # Get today's bookings
    today = timezone.now().date()
    today_bookings = Booking.objects.filter(
        booking_time__date=today
    ).count()
    
    # Get active schedules
    active_schedules = Schedule.objects.filter(
        is_active=True,
        departure_time__gte=timezone.now()
    ).count()
    
    # Get unresolved alerts
    unresolved_alerts = Alert.objects.filter(
        is_resolved=False
    ).count()
    
    return Response({
        'total_buses': total_buses,
        'active_buses': active_buses,
        'total_stations': total_stations,
        'total_routes': total_routes,
        'today_bookings': today_bookings,
        'active_schedules': active_schedules,
        'unresolved_alerts': unresolved_alerts
    })

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_bus_status(request):
    # Get all active buses with their current location and schedule
    active_buses = Bus.objects.filter(is_active=True)
    
    data = []
    for bus in active_buses:
        # Get current location
        try:
            location = BusLocation.objects.get(bus=bus)
            location_data = {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'updated_at': location.timestamp
            }
        except BusLocation.DoesNotExist:
            location_data = None
        
        # Get current or next schedule
        current_time = timezone.now()
        schedule = Schedule.objects.filter(
            bus=bus,
            is_active=True,
            departure_time__lte=current_time,
            arrival_time__gte=current_time
        ).first()
        
        if not schedule:
            # Get next schedule
            schedule = Schedule.objects.filter(
                bus=bus,
                is_active=True,
                departure_time__gt=current_time
            ).order_by('departure_time').first()
        
        if schedule:
            schedule_data = {
                'id': schedule.id,
                'start_station': schedule.start_station.name,
                'end_station': schedule.end_station.name,
                'departure_time': schedule.departure_time,
                'arrival_time': schedule.arrival_time
            }
        else:
            schedule_data = None
        
        data.append({
            'id': bus.id,
            'number': bus.number,
            'type': bus.type,
            'location': location_data,
            'current_schedule': schedule_data
        })
    
    return Response(data)