from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'date_of_birth', 'phone', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'emergency_contact']
    readonly_fields = ['created_at', 'updated_at']
