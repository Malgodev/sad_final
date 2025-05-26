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
