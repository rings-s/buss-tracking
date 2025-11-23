from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # ViewSets
    BusViewSet, RouteViewSet, TripViewSet, EmployeeBoardingViewSet,
    # Page Views
    DashboardView, LiveTrackingView, TripTrackingDetailView,
    # API Endpoints
    nfc_checkin, gps_update, bus_location_history,
    # Legacy Views
    UpdateBusLocationAPIView, StartTripAPI, EndTripAPI, ScanNFCView,
    AdminDashboardView, EmployeeAbsenceReportView
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'buses', BusViewSet, basename='bus')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'boardings', EmployeeBoardingViewSet, basename='boarding')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),

    # ==========================================================================
    # PAGE 1: DASHBOARD
    # ==========================================================================
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # ==========================================================================
    # PAGE 2: LIVE TRACKING
    # ==========================================================================
    path('live-tracking/', LiveTrackingView.as_view(), name='live-tracking'),
    path('live-tracking/<int:trip_id>/', TripTrackingDetailView.as_view(), name='trip-tracking-detail'),

    # ==========================================================================
    # API ENDPOINTS
    # ==========================================================================
    path('checkin/', nfc_checkin, name='nfc-checkin'),
    path('gps-update/', gps_update, name='gps-update'),
    path('buses/<int:bus_id>/locations/', bus_location_history, name='bus-location-history'),

    # ==========================================================================
    # LEGACY ENDPOINTS (for backward compatibility)
    # ==========================================================================
    path('location/update/', UpdateBusLocationAPIView.as_view(), name='update-location'),
    path('trip/start/', StartTripAPI.as_view(), name='start-trip'),
    path('trip/end/', EndTripAPI.as_view(), name='end-trip'),
    path('nfc/scan/', ScanNFCView.as_view(), name='scan-nfc'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/absence-report/', EmployeeAbsenceReportView.as_view(), name='absence-report'),
]
