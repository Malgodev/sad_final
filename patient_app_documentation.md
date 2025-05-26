# Patient App Documentation

## 1. Folder Structure

```
src/healthcare/patient/
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
└── migrations/
    ├── __init__.py
    └── 0001_initial.py

src/healthcare/templates/patient/
├── base.html
├── dashboard.html
├── login.html
├── register.html
├── profile.html
└── appointments/
    ├── book.html
    ├── calendar.html
    ├── cancel.html
    ├── detail.html
    └── list.html
```

## 2. Core Application Files

### a. App Configuration (apps.py)

```python
from django.apps import AppConfig


class PatientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient'
```

### b. Models (models.py)

```python
from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
```

### c. Admin Configuration (admin.py)

```python
from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'date_of_birth', 'phone', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'emergency_contact']
    readonly_fields = ['created_at', 'updated_at']
```

## 3. Forms

### a. Patient Forms (forms.py)

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Patient

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES, required=False)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    emergency_contact = forms.CharField(max_length=100, required=False)
    emergency_phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name != 'date_of_birth':
                field.widget.attrs['placeholder'] = field.label

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create patient profile
            Patient.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender', ''),
                phone=self.cleaned_data.get('phone', ''),
                address=self.cleaned_data.get('address', ''),
                emergency_contact=self.cleaned_data.get('emergency_contact', ''),
                emergency_phone=self.cleaned_data.get('emergency_phone', '')
            )
        return user

class PatientLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
        
        # Customize labels
        self.fields['username'].widget.attrs['placeholder'] = 'Username or Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

class PatientProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'gender', 'phone', 'address', 'emergency_contact', 'emergency_phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Name'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Phone'}),
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance.user if self.instance else None
        
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=user.pk if user else None).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        patient = super().save(commit=False)
        
        # Update user fields
        if patient.user:
            patient.user.first_name = self.cleaned_data['first_name']
            patient.user.last_name = self.cleaned_data['last_name']
            patient.user.email = self.cleaned_data['email']
            if commit:
                patient.user.save()
        
        if commit:
            patient.save()
        
        return patient
```

## 4. URL Configuration

### a. URL Patterns (urls.py)

```python
from django.urls import path
from . import views
from .auth_views import PatientRegistrationView, PatientLoginView, PatientAPILoginView, patient_logout
from . import appointment_views

app_name = 'patient'

urlpatterns = [
    path('', views.patient_home, name='home'),
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('profile/', views.patient_profile, name='profile'),
    path('appointments/', views.patient_appointments, name='appointments'),
    
    # Appointment Management URLs
    path('appointments/calendar/', appointment_views.patient_appointment_calendar, name='appointment_calendar'),
    path('appointments/list/', appointment_views.patient_appointment_list, name='appointment_list'),
    path('appointments/book/<int:slot_id>/', appointment_views.book_appointment, name='book_appointment'),
    path('appointments/detail/<int:appointment_id>/', appointment_views.appointment_detail, name='appointment_detail'),
    path('appointments/cancel/<int:appointment_id>/', appointment_views.cancel_appointment, name='cancel_appointment'),
    path('appointments/dashboard/', appointment_views.patient_dashboard_appointments, name='appointment_dashboard'),
    
    # API endpoints
    path('api/available-slots/', appointment_views.available_slots_api, name='available_slots_api'),
    
    # Authentication URLs
    path('register/', PatientRegistrationView.as_view(), name='register'),
    path('login/', PatientLoginView.as_view(), name='login'),
    path('logout/', patient_logout, name='logout'),
    
    # API Authentication
    path('api/login/', PatientAPILoginView.as_view(), name='api_login'),
] 