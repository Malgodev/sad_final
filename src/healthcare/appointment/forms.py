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