from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Doctor
from .forms import DoctorProfileForm
from appointment.models import Appointment

def doctor_home(request):
    return render(request, 'doctor/home.html')

@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        
        # Check if doctor is approved
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved. Please wait for admin approval.')
            return redirect('doctor:auth_login')
        
        # Get today's appointment slots
        today = timezone.now().date()
        from appointment.models import AppointmentSlot
        
        today_slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date=today
        ).prefetch_related('appointment__patient__user').order_by('slot_type')
        
        # Get upcoming booked appointments (next 7 days)
        week_end = today + timedelta(days=7)
        upcoming_slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date__gt=today,
            date__lte=week_end,
            appointment__isnull=False
        ).prefetch_related('appointment__patient__user').order_by('date', 'slot_type')[:5]
        
        # Get recent completed appointments (last 7 days)
        week_start = today - timedelta(days=7)
        recent_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date__gte=week_start,
            appointment_date__date__lt=today,
            status='completed'
        ).select_related('patient__user').order_by('-appointment_date')[:5]
        
        # Calculate statistics
        total_slots = AppointmentSlot.objects.filter(doctor=doctor).count()
        booked_slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            appointment__isnull=False
        ).count()
        available_slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            appointment__isnull=True,
            date__gte=today
        ).count()
        completed_appointments = Appointment.objects.filter(
            doctor=doctor, 
            status='completed'
        ).count()
        
        context = {
            'doctor': doctor,
            'today_slots': today_slots,
            'upcoming_slots': upcoming_slots,
            'recent_appointments': recent_appointments,
            'total_slots': total_slots,
            'booked_slots': booked_slots,
            'available_slots': available_slots,
            'completed_appointments': completed_appointments,
            'today': today,
        }
        
        return render(request, 'doctor/dashboard.html', context)
        
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administration.')
        return redirect('doctor:auth_login')

@login_required
def doctor_profile(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
        
        if request.method == 'POST':
            form = DoctorProfileForm(request.POST, instance=doctor, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('doctor:profile')
        else:
            form = DoctorProfileForm(instance=doctor, user=request.user)
        
        context = {
            'doctor': doctor,
            'form': form,
        }
        
        return render(request, 'doctor/profile.html', context)
        
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')

@login_required
def public_doctor_profile(request, doctor_id):
    """Public doctor profile view accessible by patients"""
    try:
        doctor = Doctor.objects.get(id=doctor_id, approval_status='approved')
    except Doctor.DoesNotExist:
        return render(request, 'doctor/profile_not_found.html', {
            'error': 'Doctor not found or not available.'
        })
    
    # Get doctor's available slots for the next 30 days
    from datetime import date, timedelta
    from appointment.models import AppointmentSlot
    
    today = date.today()
    end_date = today + timedelta(days=30)
    
    available_slots = AppointmentSlot.objects.filter(
        doctor=doctor,
        date__range=[today, end_date],
        appointment__isnull=True
    ).order_by('date', 'slot_type')[:10]
    
    # Get recent patient reviews/ratings (if implemented)
    # For now, we'll use placeholder data
    
    context = {
        'doctor': doctor,
        'available_slots': available_slots,
        'is_public_view': True,
    }
    
    return render(request, 'doctor/public_profile.html', context)
