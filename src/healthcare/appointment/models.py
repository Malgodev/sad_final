from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time
from doctor.models import Doctor
from patient.models import Patient

class AppointmentSlot(models.Model):
    """Available appointment slots created by doctors"""
    
    SLOT_CHOICES = [
        ('morning_1', 'Morning 8:00 - 9:30'),
        ('morning_2', 'Morning 10:00 - 11:30'),
        ('afternoon_1', 'Afternoon 1:30 - 3:00'),
        ('afternoon_2', 'Afternoon 3:30 - 5:00'),
    ]
    
    SLOT_TIMES = {
        'morning_1': (time(8, 0), time(9, 30)),
        'morning_2': (time(10, 0), time(11, 30)),
        'afternoon_1': (time(13, 30), time(15, 0)),
        'afternoon_2': (time(15, 30), time(17, 0)),
    }
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointment_slots')
    date = models.DateField()
    slot_type = models.CharField(max_length=20, choices=SLOT_CHOICES)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def start_time(self):
        return self.SLOT_TIMES[self.slot_type][0]
    
    @property
    def end_time(self):
        return self.SLOT_TIMES[self.slot_type][1]
    
    @property
    def datetime_start(self):
        return timezone.datetime.combine(self.date, self.start_time)
    
    @property
    def datetime_end(self):
        return timezone.datetime.combine(self.date, self.end_time)
    
    def __str__(self):
        return f"Dr. {self.doctor.user.get_full_name()} - {self.date} {self.get_slot_type_display()}"
    
    class Meta:
        unique_together = ['doctor', 'date', 'slot_type']
        verbose_name = "Appointment Slot"
        verbose_name_plural = "Appointment Slots"
        ordering = ['date', 'slot_type']

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_slot = models.OneToOneField(AppointmentSlot, on_delete=models.CASCADE, related_name='appointment', null=True, blank=True)
    appointment_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=90)  # Fixed 1.5 hour slots
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.patient:
            return f"{self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
        else:
            return f"Available slot - Dr. {self.doctor.user.get_full_name()} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_available(self):
        return self.patient is None

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['-appointment_date']
