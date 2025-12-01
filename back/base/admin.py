from django.contrib import admin
from .models import Bus, Route, Trip, BusLocation, BusAttendance, EmployeeBoarding


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['name', 'plate_number', 'driver', 'capacity', 'active']
    list_filter = ['active', 'driver']
    search_fields = ['name', 'plate_number', 'driver__full_name']
    list_editable = ['active']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_point', 'end_point']
    search_fields = ['name', 'start_point', 'end_point']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['id', 'bus', 'driver', 'route', 'start_time', 'end_time', 'is_active', 'boarding_count']
    list_filter = ['is_active', 'start_time', 'driver', 'bus']
    search_fields = ['bus__name', 'driver__full_name', 'route__name']
    date_hierarchy = 'start_time'
    readonly_fields = ['start_time']

    def boarding_count(self, obj):
        return obj.employeeboarding_set.count()
    boarding_count.short_description = 'Boardings'


@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ['bus', 'latitude', 'longitude', 'timestamp']
    list_filter = ['bus', 'timestamp']
    search_fields = ['bus__name']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(BusAttendance)
class BusAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'bus', 'check_in_time']
    list_filter = ['bus', 'check_in_time']
    search_fields = ['employee__full_name', 'bus__name']
    date_hierarchy = 'check_in_time'
    readonly_fields = ['check_in_time']


@admin.register(EmployeeBoarding)
class EmployeeBoardingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'trip', 'boarded_at', 'latitude', 'longitude']
    list_filter = ['boarded_at', 'trip__bus', 'trip__driver']
    search_fields = ['employee__full_name', 'trip__bus__name']
    date_hierarchy = 'boarded_at'
    readonly_fields = ['boarded_at']
