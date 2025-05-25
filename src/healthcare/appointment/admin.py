from django.contrib import admin
from .models import Appointment, AppointmentSlot

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'slot_type', 'is_available', 'has_appointment', 'created_at']
    list_filter = ['slot_type', 'date', 'is_available', 'doctor__specialization', 'created_at']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    def has_appointment(self, obj):
        return hasattr(obj, 'appointment') and obj.appointment is not None
    has_appointment.boolean = True
    has_appointment.short_description = 'Booked'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'duration_minutes', 'appointment_slot', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor__specialization', 'created_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 
                    'doctor__user__first_name', 'doctor__user__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
