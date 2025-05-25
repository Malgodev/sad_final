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