# Doctor App Documentation

## 1. Folder Structure

```
src/healthcare/doctor/
├── __init__.py
├── apps.py
├── admin.py
├── models.py
├── forms.py
├── views.py
├── auth_views.py
├── appointment_views.py
├── urls.py
├── tests.py
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── populate_sample_data.py
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_doctor_approval_status_doctor_approved_at_and_more.py

src/healthcare/templates/doctor/
├── home.html
├── dashboard.html
├── login.html
├── register.html
├── profile.html
├── public_profile.html
├── profile_not_found.html
└── appointments/
    ├── calendar.html
    ├── create_slots.html
    ├── bulk_create.html
    ├── list.html
    ├── slot_detail.html
    ├── delete_slot.html
    └── dashboard.html
```

## 2. Core Application Files

### a. App Configuration (apps.py)

```python
from django.apps import AppConfig


class DoctorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doctor'
```

### b. Models (models.py)

```python
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, default='General Medicine')
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    experience_years = models.IntegerField(default=0)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_doctors')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status_indicator = "✓" if self.approval_status == 'approved' else "⏳" if self.approval_status == 'pending' else "✗"
        return f"{status_indicator} Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"

    @property
    def is_approved(self):
        return self.approval_status == 'approved'

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
```

### c. Admin Configuration (admin.py)

```python
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
```

## 3. Forms (forms.py)

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Doctor

class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    specialization = forms.CharField(max_length=100, required=True)
    license_number = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=15, required=False)
    experience_years = forms.IntegerField(min_value=0, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if Doctor.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("A doctor with this license number already exists.")
        return license_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Doctor accounts start as inactive until approved
        
        if commit:
            user.save()
            # Create doctor profile with pending approval status
            Doctor.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                license_number=self.cleaned_data['license_number'],
                phone=self.cleaned_data.get('phone', ''),
                experience_years=self.cleaned_data['experience_years'],
                approval_status='pending'
            )
        return user

class DoctorLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
        
        # Customize labels
        self.fields['username'].widget.attrs['placeholder'] = 'Username or Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

class DoctorProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Doctor
        fields = ['specialization', 'phone', 'experience_years']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medical Specialization'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        
        # Add CSS classes for user fields
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email Address'})
        
        # Add readonly field for license number (display only)
        self.fields['license_number_display'] = forms.CharField(
            label='License Number',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'style': 'background-color: #f8f9fa;'
            })
        )
        
        if self.instance and self.instance.license_number:
            self.fields['license_number_display'].initial = self.instance.license_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance.user if self.instance else None
        
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=user.pk if user else None).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        doctor = super().save(commit=False)
        
        # Update user fields
        if doctor.user:
            doctor.user.first_name = self.cleaned_data['first_name']
            doctor.user.last_name = self.cleaned_data['last_name']
            doctor.user.email = self.cleaned_data['email']
            if commit:
                doctor.user.save()
        
        if commit:
            doctor.save()
        
        return doctor
```

## 4. URL Configuration (urls.py)

```python
from django.urls import path
from . import views
from .auth_views import DoctorRegistrationView, DoctorLoginView, DoctorAPILoginView, doctor_logout
from . import appointment_views

app_name = 'doctor'

urlpatterns = [
    path('', views.doctor_home, name='home'),
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('profile/', views.doctor_profile, name='profile'),
    
    # Public doctor profile (accessible by patients)
    path('profile/<int:doctor_id>/', views.public_doctor_profile, name='public_profile'),
    
    # Doctor Authentication URLs (separate from patient login)
    path('auth/', DoctorLoginView.as_view(), name='auth_login'),
    path('auth/register/', DoctorRegistrationView.as_view(), name='auth_register'),
    path('auth/logout/', doctor_logout, name='auth_logout'),
    
    # Appointment Slot Management URLs
    path('appointments/', appointment_views.appointment_calendar, name='appointment_calendar'),
    path('appointments/list/', appointment_views.appointment_list, name='appointment_list'),
    path('appointments/create-slots/', appointment_views.create_appointment_slots, name='create_appointment_slots'),
    path('appointments/bulk-create/', appointment_views.bulk_create_slots, name='bulk_create_slots'),
    path('appointments/slot/<int:slot_id>/', appointment_views.slot_detail, name='slot_detail'),
    path('appointments/slot/<int:slot_id>/delete/', appointment_views.delete_slot, name='delete_slot'),
    
    # Legacy appointment URLs (for backward compatibility)
    path('appointments/create/', appointment_views.create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/', appointment_views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/edit/', appointment_views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:appointment_id>/delete/', appointment_views.delete_appointment, name='delete_appointment'),
    
    # API Endpoints
    path('api/login/', DoctorAPILoginView.as_view(), name='api_login'),
    path('api/patients/search/', appointment_views.patient_search_api, name='patient_search_api'),
] 