from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Patient

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

def patient_profile(request):
    return HttpResponse("""
    <h1>Patient Profile</h1>
    <p>Patient profile management coming soon...</p>
    <a href="/patient/">Back to Patient Portal</a>
    """)

def patient_appointments(request):
    return HttpResponse("""
    <h1>My Appointments</h1>
    <p>Your appointments will be displayed here...</p>
    <a href="/patient/">Back to Patient Portal</a>
    """)
