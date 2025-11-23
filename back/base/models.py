from django.db import models
from accounts.models import User

class Bus(models.Model):
    name = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(default=50)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role':'driver'})
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.plate_number}"


class Route(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Downtown to Factory"
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.PROTECT)
    driver = models.ForeignKey(User, on_delete=models.PROTECT)
    route = models.ForeignKey(Route, on_delete=models.PROTECT, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Trip #{self.id} - {self.bus}"


class BusLocation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus} - {self.timestamp}"


class BusAttendance(models.Model):
    employee = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                                 limit_choices_to={"role": "employee"})
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    bus_location_at_checkin = models.JSONField(default=dict)


class EmployeeBoarding(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'employee'})
    boarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'employee')  # Prevent double scanning

    def __str__(self):
        return f"{self.employee} boarded at {self.boarded_at}"
