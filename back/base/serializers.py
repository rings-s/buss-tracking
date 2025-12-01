from rest_framework import serializers
from django.utils import timezone
from .models import Bus, Route, Trip, BusLocation, BusAttendance, EmployeeBoarding
from accounts.serializers import UserMinimalSerializer, DriverSerializer, EmployeeSerializer
from accounts.models import User


# =============================================================================
# BASE SERIALIZERS
# =============================================================================

class RouteSerializer(serializers.ModelSerializer):
    """Route serializer"""
    class Meta:
        model = Route
        fields = ['id', 'name', 'start_point', 'end_point']


class BusLocationSerializer(serializers.ModelSerializer):
    """GPS location point serializer"""
    class Meta:
        model = BusLocation
        fields = ['id', 'bus', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['id', 'timestamp']


# =============================================================================
# NESTED SERIALIZERS - DEBUG FRIENDLY
# =============================================================================

class BusSerializer(serializers.ModelSerializer):
    """Bus serializer with nested driver info"""
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='driver'),
        source='driver',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Bus
        fields = [
            'id', 'name', 'plate_number', 'capacity',
            'driver', 'driver_id', 'active'
        ]
        read_only_fields = ['id']

    def validate_plate_number(self, value):
        """Ensure plate number uniqueness"""
        instance = getattr(self, 'instance', None)
        if Bus.objects.filter(plate_number=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Bus with this plate number already exists.")
        return value


class EmployeeBoardingSerializer(serializers.ModelSerializer):
    """Employee boarding record with nested employee info"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='employee'),
        source='employee',
        write_only=True
    )
    bus = BusSerializer(read_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(
        queryset=Bus.objects.all(),
        source='bus',
        write_only=True
    )

    class Meta:
        model = EmployeeBoarding
        fields = ['id', 'trip', 'bus', 'bus_id', 'employee', 'employee_id', 'boarded_at', 'latitude', 'longitude']
        read_only_fields = ['id', 'boarded_at']


class BusAttendanceSerializer(serializers.ModelSerializer):
    """Bus attendance with nested relations"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='employee'),
        source='employee',
        write_only=True
    )
    bus = BusSerializer(read_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(
        queryset=Bus.objects.all(),
        source='bus',
        write_only=True
    )

    class Meta:
        model = BusAttendance
        fields = [
            'id', 'employee', 'employee_id', 'bus', 'bus_id',
            'check_in_time', 'bus_location_at_checkin'
        ]
        read_only_fields = ['id', 'check_in_time']


# =============================================================================
# TRIP SERIALIZERS - FULL NESTED FOR DEBUGGING
# =============================================================================

class TripSerializer(serializers.ModelSerializer):
    """Trip serializer with all nested relations for debugging"""
    bus = BusSerializer(read_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(
        queryset=Bus.objects.filter(active=True),
        source='bus',
        write_only=True
    )
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='driver'),
        source='driver',
        write_only=True
    )
    route = RouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        source='route',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Nested related data
    boardings = EmployeeBoardingSerializer(
        many=True,
        read_only=True,
        source='employeeboarding_set'
    )
    boarding_count = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'bus', 'bus_id', 'driver', 'driver_id',
            'route', 'route_id', 'start_time', 'end_time',
            'is_active', 'boardings', 'boarding_count', 'duration'
        ]
        read_only_fields = ['id', 'start_time']

    def get_boarding_count(self, obj):
        """Count of employees boarded on this trip"""
        return obj.employeeboarding_set.count()

    def get_duration(self, obj):
        """Trip duration in minutes"""
        if obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        elif obj.is_active:
            delta = timezone.now() - obj.start_time
            return int(delta.total_seconds() / 60)
        return None

    def validate(self, data):
        """Validate trip data"""
        bus = data.get('bus')
        driver = data.get('driver')

        # Check if bus already has active trip
        if bus and Trip.objects.filter(bus=bus, is_active=True).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError({
                'bus': 'This bus already has an active trip.'
            })

        # Check if driver already has active trip
        if driver and Trip.objects.filter(driver=driver, is_active=True).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError({
                'driver': 'This driver already has an active trip.'
            })

        return data


class TripDetailSerializer(TripSerializer):
    """Extended trip serializer with location history"""
    locations = serializers.SerializerMethodField()
    latest_location = serializers.SerializerMethodField()

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['locations', 'latest_location']

    def get_locations(self, obj):
        """Get last 50 location points for the trip's bus"""
        locations = BusLocation.objects.filter(
            bus=obj.bus,
            timestamp__gte=obj.start_time
        ).order_by('-timestamp')[:50]
        return BusLocationSerializer(locations, many=True).data

    def get_latest_location(self, obj):
        """Get most recent location"""
        location = BusLocation.objects.filter(
            bus=obj.bus,
            timestamp__gte=obj.start_time
        ).order_by('-timestamp').first()
        if location:
            return BusLocationSerializer(location).data
        return None


# =============================================================================
# PAGE-SPECIFIC SERIALIZERS
# =============================================================================

class DashboardBusSerializer(serializers.ModelSerializer):
    """Bus data for dashboard page"""
    driver = DriverSerializer(read_only=True)
    active_trip = serializers.SerializerMethodField()
    latest_location = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = [
            'id', 'name', 'plate_number', 'capacity',
            'driver', 'active', 'active_trip', 'latest_location'
        ]

    def get_active_trip(self, obj):
        """Get current active trip if any"""
        trip = Trip.objects.filter(bus=obj, is_active=True).first()
        if trip:
            return {
                'id': trip.id,
                'route': trip.route.name if trip.route else None,
                'start_time': trip.start_time,
                'boarding_count': trip.employeeboarding_set.count()
            }
        return None

    def get_latest_location(self, obj):
        """Get most recent GPS location"""
        location = BusLocation.objects.filter(bus=obj).order_by('-timestamp').first()
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'timestamp': location.timestamp
            }
        return None


class LiveTrackingSerializer(serializers.ModelSerializer):
    """Real-time tracking data for live tracking page"""
    bus = BusSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    route = RouteSerializer(read_only=True)
    current_location = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()
    recent_boardings = serializers.SerializerMethodField()
    boarding_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'bus', 'driver', 'route', 'start_time',
            'is_active', 'current_location', 'locations', 'recent_boardings', 'boarding_count'
        ]

    def get_current_location(self, obj):
        """Get current GPS location with speed and heading"""
        location = BusLocation.objects.filter(
            bus=obj.bus,
            timestamp__gte=obj.start_time
        ).order_by('-timestamp').first()
        if location:
            # Calculate heading from last two points
            heading = 0
            speed = 0
            prev_location = BusLocation.objects.filter(
                bus=obj.bus,
                timestamp__gte=obj.start_time,
                timestamp__lt=location.timestamp
            ).order_by('-timestamp').first()

            if prev_location:
                import math
                # Calculate heading (bearing) between two points
                lat1 = math.radians(prev_location.latitude)
                lat2 = math.radians(location.latitude)
                diff_lng = math.radians(location.longitude - prev_location.longitude)

                x = math.sin(diff_lng) * math.cos(lat2)
                y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(diff_lng)
                heading = math.degrees(math.atan2(x, y))
                heading = (heading + 360) % 360

                # Calculate speed (km/h)
                time_diff = (location.timestamp - prev_location.timestamp).total_seconds()
                if time_diff > 0:
                    # Haversine distance
                    R = 6371  # Earth's radius in km
                    dlat = lat2 - lat1
                    dlng = diff_lng
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    distance = R * c
                    speed = (distance / time_diff) * 3600  # km/h

            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'timestamp': location.timestamp,
                'speed': round(speed, 1),
                'heading': round(heading, 1)
            }
        return None

    def get_locations(self, obj):
        """Get all location points for the trip"""
        locations = BusLocation.objects.filter(
            bus=obj.bus,
            timestamp__gte=obj.start_time
        ).order_by('timestamp')
        return [
            {
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'timestamp': loc.timestamp
            }
            for loc in locations
        ]

    def get_recent_boardings(self, obj):
        """Last 10 employee boardings"""
        boardings = obj.employeeboarding_set.order_by('-boarded_at')[:10]
        return EmployeeBoardingSerializer(boardings, many=True).data

    def get_boarding_count(self, obj):
        return obj.employeeboarding_set.count()


# =============================================================================
# NFC CHECK-IN SERIALIZER
# =============================================================================

class NFCCheckInSerializer(serializers.Serializer):
    """NFC check-in request serializer - captures tablet GPS location"""
    nfc_uid = serializers.CharField(max_length=100)
    trip_id = serializers.IntegerField()
    # Tablet GPS location (required for attendance tracking)
    latitude = serializers.FloatField(min_value=-90, max_value=90, required=False, allow_null=True)
    longitude = serializers.FloatField(min_value=-180, max_value=180, required=False, allow_null=True)

    def validate_nfc_uid(self, value):
        """Validate NFC UID exists"""
        try:
            user = User.objects.get(nfc_uid=value, role='employee', is_active=True)
            self.employee = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or unregistered NFC card.")
        return value

    def validate_trip_id(self, value):
        """Validate trip exists and is active"""
        try:
            trip = Trip.objects.get(id=value, is_active=True)
            self.trip = trip
        except Trip.DoesNotExist:
            raise serializers.ValidationError("Trip not found or not active.")
        return value

    def validate(self, data):
        """Check for duplicate boarding"""
        if hasattr(self, 'employee') and hasattr(self, 'trip'):
            if EmployeeBoarding.objects.filter(
                trip=self.trip,
                employee=self.employee
            ).exists():
                raise serializers.ValidationError({
                    'nfc_uid': 'Employee already boarded on this trip.'
                })
        return data

    def create(self, validated_data):
        """Create employee boarding record with tablet location"""
        boarding = EmployeeBoarding.objects.create(
            trip=self.trip,
            bus=self.trip.bus,
            employee=self.employee,
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude')
        )
        return boarding


class GPSUpdateSerializer(serializers.Serializer):
    """GPS location update serializer"""
    bus_id = serializers.IntegerField()
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)

    def validate_bus_id(self, value):
        """Validate bus exists and is active"""
        try:
            bus = Bus.objects.get(id=value, active=True)
            self.bus = bus
        except Bus.DoesNotExist:
            raise serializers.ValidationError("Bus not found or inactive.")
        return value

    def create(self, validated_data):
        """Create location record"""
        location = BusLocation.objects.create(
            bus=self.bus,
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude']
        )
        return location
