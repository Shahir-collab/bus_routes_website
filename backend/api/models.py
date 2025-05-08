from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class RoutePoint(models.Model):
    route = models.ForeignKey(Route, related_name='points', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.route.name} - Point {self.order}"

class BusType(models.TextChoices):
    REGULAR = 'regular', 'Regular'
    FAST = 'fast', 'Fast'
    SUPERFAST = 'superfast', 'Superfast'

class Bus(models.Model):
    number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=BusType.choices, default=BusType.REGULAR)
    capacity = models.IntegerField()
    route = models.ForeignKey(Route, related_name='buses', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bus {self.number} ({self.type})"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, related_name='schedules', on_delete=models.CASCADE)
    start_station = models.ForeignKey(Station, related_name='departures', on_delete=models.CASCADE)
    end_station = models.ForeignKey(Station, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bus.number}: {self.start_station.name} to {self.end_station.name}"

class StationSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='station_schedules', on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.schedule.bus.number} at {self.station.name}"

class BusLocation(models.Model):
    bus = models.OneToOneField(Bus, related_name='location', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0)
    heading = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Location of {self.bus.number}"

class Alert(models.Model):
    ALERT_TYPES = [
        ('delay', 'Delay'),
        ('breakdown', 'Breakdown'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    ]
    
    bus = models.ForeignKey(Bus, related_name='alerts', on_delete=models.CASCADE, null=True, blank=True)
    station = models.ForeignKey(Station, related_name='alerts', on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.alert_type} alert for {self.bus or self.station}"

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, related_name='bookings', on_delete=models.CASCADE)
    boarding_station = models.ForeignKey(Station, related_name='boardings', on_delete=models.CASCADE)
    destination_station = models.ForeignKey(Station, related_name='destinations', on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='confirmed')
    
    def __str__(self):
        return f"Booking by {self.user.username} for {self.schedule.bus.number}"