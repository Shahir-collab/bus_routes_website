from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'admin/buses', views.AdminBusViewSet)
router.register(r'admin/stations', views.AdminStationViewSet)
router.register(r'admin/routes', views.AdminRouteViewSet)
router.register(r'admin/schedules', views.AdminScheduleViewSet)
router.register(r'admin/alerts', views.AdminAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # User API endpoints
    path('stations/', views.StationListView.as_view(), name='station-list'),
    path('buses/search/', views.search_buses, name='search-buses'),
    path('buses/<int:bus_id>/', views.get_bus_details, name='bus-details'),
    path('buses/<int:bus_id>/location/', views.get_bus_location, name='bus-location'),
    path('bookings/', views.create_booking, name='create-booking'),
    
    # Admin API endpoints
    path('admin/dashboard/stats/', views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/buses/status/', views.admin_bus_status, name='admin-bus-status'),
]