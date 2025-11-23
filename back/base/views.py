from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import Bus, BusLocation, Trip, EmployeeBoarding, Route
from .serializers import (
    BusSerializer, RouteSerializer, TripSerializer, TripDetailSerializer,
    BusLocationSerializer, EmployeeBoardingSerializer,
    DashboardBusSerializer, LiveTrackingSerializer,
    NFCCheckInSerializer, GPSUpdateSerializer
)
from accounts.models import User
from accounts.permissions import (
    IsAdmin, IsDriver, IsAdminOrDriver, IsAdminOrReadOnly, CanManageBus
)


# =============================================================================
# VIEWSETS
# =============================================================================

class BusViewSet(viewsets.ModelViewSet):
    """
    Bus CRUD operations
    - Admin: Full CRUD access
    - Driver: View all, manage assigned bus
    - Employee: View only
    """
    queryset = Bus.objects.select_related('driver').all()
    serializer_class = BusSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Driver sees only their assigned bus for write operations
        if user.role == 'driver' and self.action not in ['list', 'retrieve']:
            queryset = queryset.filter(driver=user)

        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    """
    Route CRUD operations
    - Admin: Full CRUD access
    - Others: Read only
    """
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAdminOrReadOnly]


class TripViewSet(viewsets.ModelViewSet):
    """
    Trip management with nested data
    - Admin: Full access to all trips
    - Driver: Start/end own trips, view own trips
    - Employee: View trips they're boarded on
    """
    queryset = Trip.objects.select_related(
        'bus', 'bus__driver', 'driver', 'route'
    ).prefetch_related('employeeboarding_set__employee').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        return TripSerializer

    def get_permissions(self):
        if self.action in ['create', 'start']:
            return [IsAdminOrDriver()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Role-based filtering
        if user.role == 'driver':
            queryset = queryset.filter(driver=user)
        elif user.role == 'employee':
            queryset = queryset.filter(employeeboarding__employee=user).distinct()

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        driver_id = self.request.query_params.get('driver_id')
        if driver_id and user.role == 'admin':
            queryset = queryset.filter(driver_id=driver_id)
        return queryset.order_by('-start_time')

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrDriver])
    def start(self, request):
        """Start a new trip (driver/admin only)"""
        data = request.data.copy()

        # Driver can only start trip for themselves
        if request.user.role == 'driver':
            data['driver_id'] = request.user.id
            # Get driver's assigned bus
            try:
                bus = Bus.objects.get(driver=request.user, active=True)
                data['bus_id'] = bus.id
            except Bus.DoesNotExist:
                return Response(
                    {'error': 'No active bus assigned to you'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = TripSerializer(data=data)
        if serializer.is_valid():
            trip = serializer.save()
            return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDriver])
    def end(self, request, pk=None):
        """End an active trip"""
        trip = self.get_object()

        # Driver can only end their own trip
        if request.user.role == 'driver' and trip.driver != request.user:
            return Response(
                {'error': 'You can only end your own trips'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not trip.is_active:
            return Response(
                {'error': 'Trip is already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip.is_active = False
        trip.end_time = timezone.now()
        trip.save()
        return Response(TripSerializer(trip).data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active trips"""
        trips = self.get_queryset().filter(is_active=True)
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)


class EmployeeBoardingViewSet(viewsets.ModelViewSet):
    """
    Employee boarding records
    - Admin: Full access to all records
    - Driver: View boardings for own trips
    - Employee: View own boardings
    """
    queryset = EmployeeBoarding.objects.select_related('trip', 'employee').all()
    serializer_class = EmployeeBoardingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDriver()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Role-based filtering
        if user.role == 'driver':
            queryset = queryset.filter(trip__driver=user)
        elif user.role == 'employee':
            queryset = queryset.filter(employee=user)

        trip_id = self.request.query_params.get('trip_id')
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset.order_by('-boarded_at')


# =============================================================================
# PAGE 1: DASHBOARD VIEW (Enhanced)
# =============================================================================

class DashboardView(APIView):
    """
    Dashboard page data - role-based
    GET /api/dashboard/
    - Admin: Full system overview
    - Driver: Own bus and trip stats
    - Employee: Own boarding stats
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        if user.role == 'admin':
            # Admin sees everything
            buses = Bus.objects.select_related('driver').all()
            buses_data = DashboardBusSerializer(buses, many=True).data
            active_trips = Trip.objects.filter(is_active=True).count()
            today_boardings = EmployeeBoarding.objects.filter(boarded_at__date=today).count()
            today_trips = Trip.objects.filter(start_time__date=today).count()
            buses_on_route = Trip.objects.filter(is_active=True).values('bus').distinct().count()

            return Response({
                'buses': buses_data,
                'summary': {
                    'total_buses': buses.count(),
                    'buses_on_route': buses_on_route,
                    'buses_idle': buses.filter(active=True).count() - buses_on_route,
                    'active_trips': active_trips,
                    'today_boardings': today_boardings,
                    'today_trips': today_trips,
                }
            })

        elif user.role == 'driver':
            # Driver sees own bus and trips
            try:
                bus = Bus.objects.select_related('driver').get(driver=user)
                bus_data = DashboardBusSerializer(bus).data
            except Bus.DoesNotExist:
                bus_data = None

            my_trips = Trip.objects.filter(driver=user)
            active_trip = my_trips.filter(is_active=True).first()
            today_trips = my_trips.filter(start_time__date=today).count()
            today_boardings = EmployeeBoarding.objects.filter(
                trip__driver=user, boarded_at__date=today
            ).count()

            return Response({
                'bus': bus_data,
                'active_trip': TripSerializer(active_trip).data if active_trip else None,
                'summary': {
                    'today_trips': today_trips,
                    'today_boardings': today_boardings,
                    'total_trips': my_trips.count(),
                }
            })

        else:  # Employee
            # Employee sees own boarding history
            my_boardings = EmployeeBoarding.objects.filter(employee=user)
            today_boardings = my_boardings.filter(boarded_at__date=today).count()
            recent_boardings = my_boardings.select_related(
                'trip', 'trip__bus', 'trip__driver'
            ).order_by('-boarded_at')[:5]

            return Response({
                'summary': {
                    'today_boardings': today_boardings,
                    'total_boardings': my_boardings.count(),
                },
                'recent_boardings': EmployeeBoardingSerializer(recent_boardings, many=True).data
            })


# =============================================================================
# PAGE 2: LIVE TRACKING VIEW
# =============================================================================

class LiveTrackingView(APIView):
    """
    Live tracking page data - role-based
    GET /api/live-tracking/
    - Admin: All active trips
    - Driver: Own active trip
    - Employee: Trips they're boarded on
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        active_trips = Trip.objects.filter(is_active=True).select_related(
            'bus', 'bus__driver', 'driver', 'route'
        ).prefetch_related('employeeboarding_set__employee')

        # Role-based filtering
        if user.role == 'driver':
            active_trips = active_trips.filter(driver=user)
        elif user.role == 'employee':
            active_trips = active_trips.filter(employeeboarding__employee=user).distinct()

        serializer = LiveTrackingSerializer(active_trips, many=True)
        return Response({
            'active_trips': serializer.data,
            'total_active': active_trips.count()
        })


class TripTrackingDetailView(APIView):
    """
    Single trip tracking detail
    GET /api/live-tracking/{trip_id}/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, trip_id):
        try:
            trip = Trip.objects.select_related(
                'bus', 'bus__driver', 'driver', 'route'
            ).prefetch_related('employeeboarding_set__employee').get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TripDetailSerializer(trip)
        return Response(serializer.data)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAdminOrDriver])
def nfc_checkin(request):
    """
    NFC check-in endpoint (driver/admin only)
    POST /api/checkin/
    Driver scans employee NFC card on tablet
    """
    serializer = NFCCheckInSerializer(data=request.data)
    if serializer.is_valid():
        boarding = serializer.save()
        return Response({
            'success': True,
            'message': f'{boarding.employee.full_name} checked in successfully',
            'boarding': EmployeeBoardingSerializer(boarding).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminOrDriver])
def gps_update(request):
    """
    GPS location update (driver/admin only)
    POST /api/gps-update/
    """
    data = request.data.copy()

    # Driver can only update location for their own bus
    if request.user.role == 'driver':
        try:
            bus = Bus.objects.get(driver=request.user, active=True)
            data['bus_id'] = bus.id
        except Bus.DoesNotExist:
            return Response(
                {'error': 'No active bus assigned to you'},
                status=status.HTTP_400_BAD_REQUEST
            )

    serializer = GPSUpdateSerializer(data=data)
    if serializer.is_valid():
        location = serializer.save()
        return Response({
            'success': True,
            'location': BusLocationSerializer(location).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bus_location_history(request, bus_id):
    """
    Get location history for a bus
    GET /api/buses/{bus_id}/locations/
    """
    try:
        bus = Bus.objects.get(id=bus_id)
    except Bus.DoesNotExist:
        return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)

    queryset = BusLocation.objects.filter(bus=bus).order_by('-timestamp')
    limit = int(request.query_params.get('limit', 100))
    since = request.query_params.get('since')
    if since:
        queryset = queryset.filter(timestamp__gte=since)

    locations = queryset[:limit]
    serializer = BusLocationSerializer(locations, many=True)
    return Response({'bus_id': bus_id, 'locations': serializer.data})


# =============================================================================
# EXISTING VIEWS (Legacy)
# =============================================================================

# 👉 A) API: Update Bus GPS Location
class UpdateBusLocationAPIView(APIView):
    permission_classes = [IsDriver]

    def post(self, request):
        bus_id = request.data.get("bus_id")
        lat = request.data.get("latitude")
        lng = request.data.get("longitude")

        try:
            bus = Bus.objects.get(id=bus_id, driver=request.user)
        except Bus.DoesNotExist:
            return Response({"detail": "Invalid bus"}, status=404)

        BusLocation.objects.create(
            bus=bus,
            latitude=lat,
            longitude=lng,
        )

        return Response({"status": "Location updated"})




class StartTripAPI(APIView):
    permission_classes = [IsDriver]

    def post(self, request):
        bus_id = request.data.get("bus_id")
        bus = Bus.objects.get(id=bus_id)

        trip = Trip.objects.create(
            bus=bus,
            driver=request.user,
            is_active=True
        )

        return Response({"message": "Trip started", "trip_id": trip.id})


class EndTripAPI(APIView):
    permission_classes = [IsDriver]

    def post(self, request):
        trip_id = request.data.get("trip_id")
        trip = Trip.objects.get(id=trip_id, driver=request.user)

        trip.end_time = timezone.now()
        trip.is_active = False
        trip.save()

        return Response({"message": "Trip ended"})


# 👉 C) API: Employee Boarding via NFC

class ScanNFCView(APIView):
    permission_classes = [IsAdminOrDriver]  # Only driver and admin

    def post(self, request):
        # Data from SvelteKit
        nfc_uid = request.data.get('nfc_uid')
        trip_id = request.data.get('trip_id')

        # 1. Identify Employee
        employee = get_object_or_404(User, nfc_uid=nfc_uid, role='employee')

        # 2. Identify Active Trip
        trip = get_object_or_404(Trip, id=trip_id, is_active=True)

        # 3. Record Attendance (prevent duplicates)
        boarding, created = EmployeeBoarding.objects.get_or_create(
            trip=trip,
            employee=employee
        )

        if created:
            return Response(
                {"message": f"Checked in {employee.full_name}"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "Already checked in"},
                status=status.HTTP_200_OK
            )


# 👉 D) API: Admin Dashboard - System Overview
class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        
        from django.db.models import Count, Q
        from datetime import timedelta
        from django.utils import timezone
        
        # Get current time
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        
        # 1. Total Counts
        total_buses = Bus.objects.count()
        total_drivers = User.objects.filter(role='driver').count()
        total_employees = User.objects.filter(role='employee').count()
        total_routes = Route.objects.count()
        
        # 2. Active Trips
        active_trips = Trip.objects.filter(is_active=True).select_related('bus', 'driver', 'route')
        active_trips_data = [{
            'id': trip.id,
            'bus': str(trip.bus),
            'driver': trip.driver.full_name,
            'route': str(trip.route) if trip.route else 'No route assigned',
            'start_time': trip.start_time,
            'employees_boarded': EmployeeBoarding.objects.filter(trip=trip).count()
        } for trip in active_trips]
        
        # 3. Today's Statistics
        today_trips = Trip.objects.filter(start_time__gte=today_start).count()
        today_boardings = EmployeeBoarding.objects.filter(boarded_at__gte=today_start).count()
        
        # 4. Recent Activity (Last 7 days)
        recent_trips = Trip.objects.filter(start_time__gte=week_ago).count()
        recent_boardings = EmployeeBoarding.objects.filter(boarded_at__gte=week_ago).count()
        
        # 5. Bus Utilization
        buses_in_use = Bus.objects.filter(
            id__in=Trip.objects.filter(is_active=True).values_list('bus_id', flat=True)
        ).count()
        
        # 6. Top Active Buses (by trip count)
        top_buses = Bus.objects.annotate(
            trip_count=Count('trip')
        ).order_by('-trip_count')[:5]
        
        top_buses_data = [{
            'name': bus.name,
            'plate_number': bus.plate_number,
            'trip_count': bus.trip_count,
            'capacity': bus.capacity
        } for bus in top_buses]
        
        # 7. Recent Trips (Last 10)
        recent_trips_list = Trip.objects.select_related('bus', 'driver', 'route').order_by('-start_time')[:10]
        recent_trips_data = [{
            'id': trip.id,
            'bus': str(trip.bus),
            'driver': trip.driver.full_name,
            'route': str(trip.route) if trip.route else 'No route',
            'start_time': trip.start_time,
            'end_time': trip.end_time,
            'is_active': trip.is_active,
            'total_boardings': EmployeeBoarding.objects.filter(trip=trip).count()
        } for trip in recent_trips_list]
        
        # Compile dashboard data
        dashboard_data = {
            'overview': {
                'total_buses': total_buses,
                'total_drivers': total_drivers,
                'total_employees': total_employees,
                'total_routes': total_routes,
                'buses_in_use': buses_in_use,
            },
            'today': {
                'trips': today_trips,
                'boardings': today_boardings,
            },
            'last_7_days': {
                'trips': recent_trips,
                'boardings': recent_boardings,
            },
            'active_trips': active_trips_data,
            'top_buses': top_buses_data,
            'recent_trips': recent_trips_data,
        }
        
        return Response(dashboard_data)


# 👉 E) API: Employee Absence Report
class EmployeeAbsenceReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        
        from django.db.models import Q, Count
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Get query parameters
        report_type = request.query_params.get('type', 'day')  # 'day', 'month', 'range'
        date_str = request.query_params.get('date')  # Format: YYYY-MM-DD
        month_str = request.query_params.get('month')  # Format: YYYY-MM
        start_date_str = request.query_params.get('start_date')  # Format: YYYY-MM-DD
        end_date_str = request.query_params.get('end_date')  # Format: YYYY-MM-DD
        employee_id = request.query_params.get('employee_id')  # Optional: specific employee
        
        try:
            if report_type == 'day':
                # Daily absence report
                if not date_str:
                    return Response({"error": "date parameter required (YYYY-MM-DD)"}, status=400)
                
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_datetime = datetime.combine(target_date, datetime.min.time())
                end_datetime = datetime.combine(target_date, datetime.max.time())
                
                # Make timezone aware
                from django.utils import timezone as tz
                start_datetime = tz.make_aware(start_datetime)
                end_datetime = tz.make_aware(end_datetime)
                
            elif report_type == 'month':
                # Monthly absence report
                if not month_str:
                    return Response({"error": "month parameter required (YYYY-MM)"}, status=400)
                
                year, month = map(int, month_str.split('-'))
                first_day = datetime(year, month, 1)
                
                # Get last day of month
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                
                from django.utils import timezone as tz
                start_datetime = tz.make_aware(datetime.combine(first_day, datetime.min.time()))
                end_datetime = tz.make_aware(datetime.combine(last_day, datetime.max.time()))
                
            elif report_type == 'range':
                # Custom date range report
                if not start_date_str or not end_date_str:
                    return Response({"error": "start_date and end_date parameters required (YYYY-MM-DD)"}, status=400)
                
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                from django.utils import timezone as tz
                start_datetime = tz.make_aware(datetime.combine(start_date, datetime.min.time()))
                end_datetime = tz.make_aware(datetime.combine(end_date, datetime.max.time()))
            else:
                return Response({"error": "Invalid report type. Use 'day', 'month', or 'range'"}, status=400)
            
            # Get all trips in the date range
            trips_in_range = Trip.objects.filter(
                start_time__gte=start_datetime,
                start_time__lte=end_datetime
            )
            
            # Get all employees (or specific employee)
            employees_query = User.objects.filter(role='employee')
            if employee_id:
                employees_query = employees_query.filter(id=employee_id)
            
            all_employees = list(employees_query.values('id', 'full_name', 'email', 'phone_number'))
            
            # Get all employee boardings in the date range
            boardings = EmployeeBoarding.objects.filter(
                trip__in=trips_in_range
            ).values_list('employee_id', 'trip_id')
            
            # Create a set of (employee_id, trip_id) for quick lookup
            boarded_set = set(boardings)
            
            # Track absences
            absence_data = []
            attendance_summary = defaultdict(lambda: {'present': 0, 'absent': 0, 'trips': []})
            
            # For each trip, check which employees were absent
            for trip in trips_in_range.select_related('bus', 'driver', 'route'):
                for employee in all_employees:
                    employee_id_val = employee['id']
                    
                    if (employee_id_val, trip.id) not in boarded_set:
                        # Employee was absent
                        attendance_summary[employee_id_val]['absent'] += 1
                        attendance_summary[employee_id_val]['trips'].append({
                            'trip_id': trip.id,
                            'date': trip.start_time.date().isoformat(),
                            'time': trip.start_time.time().isoformat(),
                            'bus': str(trip.bus),
                            'route': str(trip.route) if trip.route else 'No route'
                        })
                    else:
                        # Employee was present
                        attendance_summary[employee_id_val]['present'] += 1
            
            # Compile absence report
            for employee in all_employees:
                emp_id = employee['id']
                summary = attendance_summary[emp_id]
                
                absence_data.append({
                    'employee_id': emp_id,
                    'full_name': employee['full_name'],
                    'email': employee['email'],
                    'phone_number': employee['phone_number'],
                    'total_trips': trips_in_range.count(),
                    'present_count': summary['present'],
                    'absent_count': summary['absent'],
                    'attendance_rate': round((summary['present'] / trips_in_range.count() * 100), 2) if trips_in_range.count() > 0 else 0,
                    'missed_trips': summary['trips'] if summary['absent'] > 0 else []
                })
            
            # Sort by absent count (most absences first)
            absence_data.sort(key=lambda x: x['absent_count'], reverse=True)
            
            # Calculate overall statistics
            total_employees = len(all_employees)
            total_trips = trips_in_range.count()
            total_possible_attendances = total_employees * total_trips
            total_actual_attendances = len(boarded_set)
            total_absences = total_possible_attendances - total_actual_attendances
            
            response_data = {
                'report_type': report_type,
                'date_range': {
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                },
                'statistics': {
                    'total_employees': total_employees,
                    'total_trips': total_trips,
                    'total_possible_attendances': total_possible_attendances,
                    'total_actual_attendances': total_actual_attendances,
                    'total_absences': total_absences,
                    'overall_attendance_rate': round((total_actual_attendances / total_possible_attendances * 100), 2) if total_possible_attendances > 0 else 0
                },
                'absences': absence_data
            }
            
            return Response(response_data)
            
        except ValueError as e:
            return Response({"error": f"Invalid date format: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
