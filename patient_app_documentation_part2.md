# Patient App Documentation - Part 2

## 5. Views

### a. Main Views (views.py)

```python
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .forms import PatientProfileForm

def patient_home(request):
    return HttpResponse("""
    <h1>Patient Portal - Hello World</h1>
    <p>Welcome to the Patient Portal!</p>
    <ul>
        <li><a href="/patient/dashboard/">Dashboard</a></li>
        <li><a href="/patient/profile/">Profile</a></li>
        <li><a href="/patient/appointments/">My Appointments</a></li>
        <li><a href="/">Back to Home</a></li>
    </ul>
    """)

@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
        
        # Import here to avoid circular imports
        from appointment.models import Appointment
        from datetime import date, timedelta
        
        # Get upcoming appointments (next 7 days)
        today = date.today()
        next_week = today + timedelta(days=7)
        
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_slot__date__range=[today, next_week],
            status__in=['scheduled', 'confirmed']
        ).select_related('appointment_slot', 'doctor', 'doctor__user').order_by('appointment_slot__date', 'appointment_slot__slot_type')[:3]
        
        # Get appointment statistics
        total_appointments = Appointment.objects.filter(patient=patient).count()
        completed_appointments = Appointment.objects.filter(patient=patient, status='completed').count()
        
        context = {
            'patient': patient,
            'upcoming_appointments': upcoming_appointments,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
        }
        
        return render(request, 'patient/dashboard.html', context)
        
    except Patient.DoesNotExist:
        return render(request, 'patient/profile_setup.html')

@login_required
def patient_profile(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:dashboard')
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('patient:profile')
    else:
        form = PatientProfileForm(instance=patient, user=request.user)
    
    context = {
        'patient': patient,
        'form': form,
    }
    
    return render(request, 'patient/profile.html', context)

def patient_appointments(request):
    return HttpResponse("""
    <h1>My Appointments</h1>
    <p>Your appointments will be displayed here...</p>
    <a href="/patient/">Back to Patient Portal</a>
    """)
```

### b. Authentication Views (auth_views.py)

```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import PatientRegistrationForm, PatientLoginForm
from .models import Patient
import json

class PatientRegistrationView(View):
    def get(self, request):
        form = PatientRegistrationForm()
        return render(request, 'patient/register.html', {
            'form': form,
            'user_type': 'Patient',
            'login_url': '/patient/login/',
            'title': 'Patient Registration'
        })

    def post(self, request):
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Patient account created successfully! Please log in.')
            return redirect('patient:login')
        return render(request, 'patient/register.html', {
            'form': form,
            'user_type': 'Patient',
            'login_url': '/patient/login/',
            'title': 'Patient Registration'
        })

class PatientLoginView(View):
    def get(self, request):
        form = PatientLoginForm()
        return render(request, 'patient/login.html', {
            'form': form,
            'user_type': 'Patient',
            'register_url': '/patient/register/',
            'title': 'Patient Login'
        })

    def post(self, request):
        form = PatientLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is a patient
                try:
                    patient = Patient.objects.get(user=user)
                    login(request, user)
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    # Store tokens in session for web interface
                    request.session['access_token'] = str(access_token)
                    request.session['refresh_token'] = str(refresh)
                    
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('patient:dashboard')
                except Patient.DoesNotExist:
                    messages.error(request, 'This account is not registered as a patient.')
            else:
                messages.error(request, 'Invalid username or password.')
        
        return render(request, 'patient/login.html', {
            'form': form,
            'user_type': 'Patient',
            'register_url': '/patient/register/',
            'title': 'Patient Login'
        })

@method_decorator(csrf_exempt, name='dispatch')
class PatientAPILoginView(View):
    """API endpoint for patient login that returns JWT tokens"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({
                    'error': 'Username and password are required'
                }, status=400)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                try:
                    patient = Patient.objects.get(user=user)
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    return JsonResponse({
                        'access_token': str(access_token),
                        'refresh_token': str(refresh),
                        'user_type': 'patient',
                        'user_id': user.id,
                        'patient_id': patient.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'gender': patient.get_gender_display() if patient.gender else None
                    })
                except Patient.DoesNotExist:
                    return JsonResponse({
                        'error': 'This account is not registered as a patient'
                    }, status=403)
            else:
                return JsonResponse({
                    'error': 'Invalid credentials'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred during login'
            }, status=500)

def patient_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('patient:login')
```

## 6. Appointment Views (appointment_views.py)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta, datetime
from calendar import monthrange
import calendar

from .models import Patient
from doctor.models import Doctor
from appointment.models import AppointmentSlot, Appointment


@login_required
def patient_appointment_calendar(request):
    """Display calendar with available appointment slots"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:profile')
    
    # Get current month/year from request or use current
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Calculate previous and next month
    if month == 1:
        prev_month = {'year': year - 1, 'month': 12}
    else:
        prev_month = {'year': year, 'month': month - 1}
    
    if month == 12:
        next_month = {'year': year + 1, 'month': 1}
    else:
        next_month = {'year': year, 'month': month + 1}
    
    # Get first and last day of month
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get calendar days (including previous/next month days for full weeks)
    cal = calendar.monthcalendar(year, month)
    calendar_days = []
    
    for week in cal:
        for day in week:
            if day == 0:
                calendar_days.append(None)
            else:
                calendar_days.append(date(year, month, day))
    
    # Get available appointment slots for the month
    available_slots = AppointmentSlot.objects.filter(
        date__range=[first_day, last_day],
        date__gte=date.today()  # Only future dates
    ).select_related('doctor', 'doctor__user').prefetch_related('appointment')
    
    # Filter only available slots (no appointment booked)
    available_slots = [slot for slot in available_slots if not hasattr(slot, 'appointment')]
    
    # Get patient's current appointments for the month
    patient_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_slot__date__range=[first_day, last_day]
    ).select_related('appointment_slot', 'doctor', 'doctor__user')
    
    # Get doctor filter
    doctor_filter = request.GET.get('doctor')
    doctors = Doctor.objects.filter(approval_status='approved').select_related('user')
    
    if doctor_filter:
        available_slots = [slot for slot in available_slots if str(slot.doctor.id) == doctor_filter]
    
    context = {
        'patient': patient,
        'current_month': first_day,
        'prev_month': prev_month,
        'next_month': next_month,
        'calendar_days': calendar_days,
        'available_slots': available_slots,
        'patient_appointments': patient_appointments,
        'doctors': doctors,
        'selected_doctor': doctor_filter,
        'today': date.today(),
    }
    
    return render(request, 'patient/appointments/calendar.html', context)


@login_required
def patient_appointment_list(request):
    """Display list of patient's current appointments"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:profile')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date')
    
    # Base query
    appointments = Appointment.objects.filter(patient=patient).select_related(
        'appointment_slot', 'doctor', 'doctor__user'
    ).order_by('-appointment_date')
    
    # Apply filters
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(appointment_slot__date=filter_date)
        except ValueError:
            pass
    
    # Separate upcoming and past appointments
    today = date.today()
    upcoming_appointments = appointments.filter(appointment_slot__date__gte=today)
    past_appointments = appointments.filter(appointment_slot__date__lt=today)
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'patient/appointments/list.html', context)


@login_required
def book_appointment(request, slot_id):
    """Book an appointment slot"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:profile')
    
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    
    # Check if slot is available
    if hasattr(slot, 'appointment'):
        messages.error(request, "This appointment slot is no longer available.")
        return redirect('patient:appointment_calendar')
    
    # Check if slot is in the future
    if slot.date < date.today():
        messages.error(request, "Cannot book appointments for past dates.")
        return redirect('patient:appointment_calendar')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, "Please provide a reason for the appointment.")
            return render(request, 'patient/appointments/book.html', {
                'patient': patient,
                'slot': slot,
            })
        
        # Create the appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=slot.doctor,
            appointment_slot=slot,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(slot.date, slot.start_time)
            ),
            status='scheduled',
            reason=reason
        )
        
        messages.success(request, f"Appointment booked successfully with Dr. {slot.doctor.user.get_full_name()} on {slot.date} at {slot.start_time}.")
        return redirect('patient:appointment_list')
    
    context = {
        'patient': patient,
        'slot': slot,
    }
    
    return render(request, 'patient/appointments/book.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View appointment details"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:profile')
    
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=patient
    )
    
    context = {
        'patient': patient,
        'appointment': appointment,
    }
    
    return render(request, 'patient/appointments/detail.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Please complete your patient profile first.")
        return redirect('patient:profile')
    
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=patient
    )
    
    # Check if appointment can be cancelled
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, "This appointment cannot be cancelled.")
        return redirect('patient:appointment_list')
    
    # Check if appointment is in the future (allow cancellation up to 2 hours before)
    appointment_datetime = timezone.make_aware(
        timezone.datetime.combine(appointment.appointment_slot.date, appointment.appointment_slot.start_time)
    )
    
    if appointment_datetime <= timezone.now() + timedelta(hours=2):
        messages.error(request, "Cannot cancel appointments less than 2 hours before the scheduled time.")
        return redirect('patient:appointment_list')
    
    if request.method == 'POST':
        # Update appointment status
        appointment.status = 'cancelled'
        appointment.notes = f"Cancelled by patient on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        appointment.save()
        
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('patient:appointment_list')
    
    context = {
        'patient': patient,
        'appointment': appointment,
    }
    
    return render(request, 'patient/appointments/cancel.html', context)


@login_required
def available_slots_api(request):
    """API endpoint to get available slots for a specific date and doctor"""
    date_str = request.GET.get('date')
    doctor_id = request.GET.get('doctor_id')
    
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Check if date is in the future
    if slot_date < date.today():
        return JsonResponse({'slots': []})
    
    # Base query for available slots
    slots_query = AppointmentSlot.objects.filter(date=slot_date).select_related('doctor', 'doctor__user')
    
    # Filter by doctor if specified
    if doctor_id:
        slots_query = slots_query.filter(doctor_id=doctor_id)
    
    # Get only available slots (no appointment booked)
    available_slots = []
    for slot in slots_query:
        if not hasattr(slot, 'appointment'):
            available_slots.append({
                'id': slot.id,
                'doctor_name': slot.doctor.user.get_full_name(),
                'doctor_specialization': slot.doctor.specialization,
                'slot_type': slot.slot_type,
                'slot_display': slot.get_slot_type_display(),
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
            })
    
    return JsonResponse({'slots': available_slots})


@login_required
def patient_dashboard_appointments(request):
    """Dashboard view showing upcoming appointments and quick actions"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient:profile')
    
    # Get upcoming appointments (next 7 days)
    today = date.today()
    next_week = today + timedelta(days=7)
    
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_slot__date__range=[today, next_week],
        status__in=['scheduled', 'confirmed']
    ).select_related('appointment_slot', 'doctor', 'doctor__user').order_by('appointment_slot__date', 'appointment_slot__slot_type')
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_slot__date__lt=today
    ).select_related('appointment_slot', 'doctor', 'doctor__user').order_by('-appointment_slot__date')[:3]
    
    # Get appointment statistics
    total_appointments = Appointment.objects.filter(patient=patient).count()
    completed_appointments = Appointment.objects.filter(patient=patient, status='completed').count()
    cancelled_appointments = Appointment.objects.filter(patient=patient, status='cancelled').count()
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    
    return render(request, 'patient/appointments/dashboard.html', context)
```

## 7. Tests

### a. Test File (tests.py)

```python
from django.test import TestCase

# Create your tests here.
```

## 8. Database Migrations

### a. Initial Migration (migrations/0001_initial.py)

```python
# Generated by Django 4.2.21 on 2025-05-25 10:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('address', models.TextField(blank=True)),
                ('emergency_contact', models.CharField(blank=True, max_length=100)),
                ('emergency_phone', models.CharField(blank=True, max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
            },
        ),
    ]
``` 