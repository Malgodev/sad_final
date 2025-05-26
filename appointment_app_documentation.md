# Appointment App Documentation

## 1. Folder Structure

```
src/healthcare/appointment/
├── __init__.py
├── apps.py
├── admin.py
├── models.py
├── forms.py
├── views.py
├── chatbot.py
├── urls.py
├── tests.py
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_alter_appointment_duration_minutes_and_more.py

src/healthcare/templates/appointment/
├── chatbot.html
└── chatbot_error.html
```

## 2. Core Application Files

### a. App Configuration (apps.py)

```python
from django.apps import AppConfig


class AppointmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointment'
```

### b. Models (models.py)

```python
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
```

### c. Admin Configuration (admin.py)

```python
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
```

## 3. Forms (forms.py)

```python
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Appointment, AppointmentSlot
from patient.models import Patient

class AppointmentSlotForm(forms.ModelForm):
    """Form for doctors to create appointment slots"""
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().strftime('%Y-%m-%d')
        }),
        help_text="Select the date for appointment slots"
    )
    
    slots = forms.MultipleChoiceField(
        choices=AppointmentSlot.SLOT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Select which time slots to make available"
    )
    
    class Meta:
        model = AppointmentSlot
        fields = ['date']
    
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
    
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        
        if selected_date:
            # Check if date is in the past
            if selected_date < timezone.now().date():
                raise forms.ValidationError("Cannot create slots for past dates.")
        
        return selected_date
    
    def save(self, commit=True):
        selected_date = self.cleaned_data['date']
        selected_slots = self.cleaned_data['slots']
        
        created_slots = []
        
        if commit and self.doctor:
            for slot_type in selected_slots:
                # Check if slot already exists
                existing_slot = AppointmentSlot.objects.filter(
                    doctor=self.doctor,
                    date=selected_date,
                    slot_type=slot_type
                ).first()
                
                if not existing_slot:
                    slot = AppointmentSlot.objects.create(
                        doctor=self.doctor,
                        date=selected_date,
                        slot_type=slot_type,
                        is_available=True
                    )
                    created_slots.append(slot)
        
        return created_slots

class BulkSlotCreationForm(forms.Form):
    """Form for creating multiple appointment slots across date range"""
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().strftime('%Y-%m-%d')
        }),
        help_text="Start date for slot creation"
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().strftime('%Y-%m-%d')
        }),
        help_text="End date for slot creation"
    )
    
    days_of_week = forms.MultipleChoiceField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        initial=[0, 1, 2, 3, 4],  # Default to weekdays
        help_text="Select days of the week"
    )
    
    slots = forms.MultipleChoiceField(
        choices=AppointmentSlot.SLOT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        initial=['afternoon_1', 'afternoon_2'],  # Default to afternoon slots
        help_text="Select which time slots to create"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date.")
            
            # Limit to 3 months to prevent excessive slot creation
            if (end_date - start_date).days > 90:
                raise forms.ValidationError("Date range cannot exceed 3 months.")
        
        return cleaned_data

class AppointmentStatusForm(forms.ModelForm):
    """Form for updating appointment status and notes"""
    
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Update appointment notes...'
            }),
        }

# Keep legacy forms for backward compatibility during transition
class AppointmentForm(forms.ModelForm):
    """Legacy form - will be deprecated"""
    
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'reason', 'notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'readonly': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for appointment...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }
```

## 4. URL Configuration (urls.py)

```python
from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.appointment_home, name='home'),
    path('list/', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
    
    # Chatbot URLs
    path('chatbot/', views.appointment_chatbot, name='chatbot'),
    path('api/chatbot/analyze/', views.chatbot_analyze, name='chatbot_analyze'),
    path('api/chatbot/suggestions/', views.chatbot_suggestions, name='chatbot_suggestions'),
    path('api/specialization/<str:specialization>/', views.specialization_info, name='specialization_info'),
    path('api/specialization/<str:specialization>/doctors/', views.specialization_doctors_links, name='specialization_doctors_links'),
    path('api/doctor/<int:doctor_id>/availability/', views.doctor_availability, name='doctor_availability'),
]
``` 