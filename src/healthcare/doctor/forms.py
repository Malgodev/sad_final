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