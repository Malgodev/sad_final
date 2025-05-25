from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'approval_status', 'experience_years', 'created_at']
    list_filter = ['approval_status', 'specialization', 'experience_years', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'license_number', 'specialization']
    readonly_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at']
    
    fieldsets = (
        ('Doctor Information', {
            'fields': ('user', 'specialization', 'license_number', 'phone', 'experience_years')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_doctors', 'reject_doctors']
    
    def approve_doctors(self, request, queryset):
        updated = 0
        for doctor in queryset.filter(approval_status='pending'):
            doctor.approval_status = 'approved'
            doctor.approved_by = request.user
            doctor.approved_at = timezone.now()
            doctor.user.is_active = True  # Activate the user account
            doctor.user.save()
            doctor.save()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} doctor(s) have been approved.',
            messages.SUCCESS
        )
    approve_doctors.short_description = "Approve selected doctors"
    
    def reject_doctors(self, request, queryset):
        updated = 0
        for doctor in queryset.filter(approval_status='pending'):
            doctor.approval_status = 'rejected'
            doctor.user.is_active = False  # Deactivate the user account
            doctor.user.save()
            doctor.save()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} doctor(s) have been rejected.',
            messages.WARNING
        )
    reject_doctors.short_description = "Reject selected doctors"
    
    def save_model(self, request, obj, form, change):
        if change and 'approval_status' in form.changed_data:
            if obj.approval_status == 'approved':
                obj.approved_by = request.user
                obj.approved_at = timezone.now()
                obj.user.is_active = True
                obj.user.save()
            elif obj.approval_status == 'rejected':
                obj.user.is_active = False
                obj.user.save()
        super().save_model(request, obj, form, change)
