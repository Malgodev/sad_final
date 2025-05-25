from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time, date
from calendar import monthrange
import json

from .models import Doctor
from appointment.models import Appointment, AppointmentSlot
from appointment.forms import AppointmentSlotForm, BulkSlotCreationForm, AppointmentStatusForm
from patient.models import Patient

@login_required
def appointment_calendar(request):
    """Main calendar view for doctor appointment slots"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        
        # Check if doctor is approved
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved. Please wait for admin approval.')
            return redirect('doctor:auth_login')
        
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    # Get current month and year
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Calculate month boundaries
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get appointment slots for the month
    slots = AppointmentSlot.objects.filter(
        doctor=doctor,
        date__gte=first_day,
        date__lte=last_day
    ).prefetch_related('appointment__patient__user').order_by('date', 'slot_type')
    
    # Group slots by date
    slots_by_date = {}
    for slot in slots:
        if slot.date not in slots_by_date:
            slots_by_date[slot.date] = []
        slots_by_date[slot.date].append(slot)
    
    # Calculate navigation dates
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    # Get today's slots
    today_slots = slots.filter(date=today)
    
    # Get upcoming slots (next 7 days)
    week_end = today + timedelta(days=7)
    upcoming_slots = slots.filter(
        date__gt=today,
        date__lte=week_end
    )[:5]
    
    context = {
        'doctor': doctor,
        'slots': slots,
        'slots_by_date': slots_by_date,
        'today_slots': today_slots,
        'upcoming_slots': upcoming_slots,
        'current_month': first_day,
        'prev_month': prev_month,
        'next_month': next_month,
        'today': today,
        'calendar_days': generate_calendar_days(year, month),
    }
    
    return render(request, 'doctor/appointments/calendar.html', context)

@login_required
def create_appointment_slots(request):
    """Create new appointment slots"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    if request.method == 'POST':
        form = AppointmentSlotForm(request.POST, doctor=doctor)
        if form.is_valid():
            created_slots = form.save()
            if created_slots:
                messages.success(request, f'Successfully created {len(created_slots)} appointment slots!')
            else:
                messages.warning(request, 'No new slots were created. They may already exist.')
            return redirect('doctor:appointment_calendar')
    else:
        form = AppointmentSlotForm(doctor=doctor)
        
        # Pre-fill date if provided
        if 'date' in request.GET:
            try:
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                form.fields['date'].initial = date_obj
            except ValueError:
                pass
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': 'Create Appointment Slots'
    }
    
    return render(request, 'doctor/appointments/create_slots.html', context)

@login_required
def bulk_create_slots(request):
    """Create multiple appointment slots across date range"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    if request.method == 'POST':
        form = BulkSlotCreationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            days_of_week = [int(d) for d in form.cleaned_data['days_of_week']]
            slot_types = form.cleaned_data['slots']
            
            created_count = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Check if current date's weekday is selected
                if current_date.weekday() in days_of_week:
                    for slot_type in slot_types:
                        # Check if slot already exists
                        existing_slot = AppointmentSlot.objects.filter(
                            doctor=doctor,
                            date=current_date,
                            slot_type=slot_type
                        ).first()
                        
                        if not existing_slot:
                            AppointmentSlot.objects.create(
                                doctor=doctor,
                                date=current_date,
                                slot_type=slot_type,
                                is_available=True
                            )
                            created_count += 1
                
                current_date += timedelta(days=1)
            
            messages.success(request, f'Successfully created {created_count} appointment slots!')
            return redirect('doctor:appointment_calendar')
    else:
        form = BulkSlotCreationForm()
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': 'Bulk Create Appointment Slots'
    }
    
    return render(request, 'doctor/appointments/bulk_create.html', context)

@login_required
def slot_detail(request, slot_id):
    """View appointment slot details"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    slot = get_object_or_404(AppointmentSlot, id=slot_id, doctor=doctor)
    
    # Get associated appointment if exists
    appointment = getattr(slot, 'appointment', None)
    
    # Handle status update for booked appointments
    if request.method == 'POST' and appointment:
        status_form = AppointmentStatusForm(request.POST, instance=appointment)
        if status_form.is_valid():
            status_form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('doctor:slot_detail', slot_id=slot.id)
    else:
        status_form = AppointmentStatusForm(instance=appointment) if appointment else None
    
    context = {
        'slot': slot,
        'appointment': appointment,
        'status_form': status_form,
        'doctor': doctor,
    }
    
    return render(request, 'doctor/appointments/slot_detail.html', context)

@login_required
def delete_slot(request, slot_id):
    """Delete appointment slot"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    slot = get_object_or_404(AppointmentSlot, id=slot_id, doctor=doctor)
    
    # Check if slot has a booked appointment
    if hasattr(slot, 'appointment') and slot.appointment.patient:
        messages.error(request, 'Cannot delete a slot that has a booked appointment. Cancel the appointment first.')
        return redirect('doctor:slot_detail', slot_id=slot.id)
    
    if request.method == 'POST':
        slot_info = f"{slot.get_slot_type_display()} on {slot.date}"
        slot.delete()
        messages.success(request, f'Appointment slot {slot_info} has been deleted.')
        return redirect('doctor:appointment_calendar')
    
    context = {
        'slot': slot,
        'doctor': doctor,
    }
    
    return render(request, 'doctor/appointments/delete_slot.html', context)

@login_required
def appointment_list(request):
    """List all appointment slots with filtering"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.error(request, 'Your account is not yet approved.')
            return redirect('doctor:auth_login')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctor:auth_login')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    slot_type_filter = request.GET.get('slot_type', '')
    
    # Base queryset
    slots = AppointmentSlot.objects.filter(doctor=doctor).prefetch_related('appointment__patient__user')
    
    # Apply filters
    if status_filter == 'available':
        slots = slots.filter(appointment__isnull=True)
    elif status_filter == 'booked':
        slots = slots.filter(appointment__isnull=False)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            slots = slots.filter(date=filter_date)
        except ValueError:
            pass
    
    if slot_type_filter:
        slots = slots.filter(slot_type=slot_type_filter)
    
    # Order by date and slot type
    slots = slots.order_by('-date', 'slot_type')
    
    context = {
        'slots': slots,
        'doctor': doctor,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'slot_type_filter': slot_type_filter,
        'slot_choices': AppointmentSlot.SLOT_CHOICES,
    }
    
    return render(request, 'doctor/appointments/list.html', context)

def generate_calendar_days(year, month):
    """Generate calendar days for the given month"""
    import calendar
    
    # Get the first day of the month and number of days
    first_day = date(year, month, 1)
    num_days = monthrange(year, month)[1]
    
    # Get the weekday of the first day (0=Monday, 6=Sunday)
    first_weekday = first_day.weekday()
    
    # Generate calendar days
    days = []
    
    # Add empty days for the beginning of the month
    for i in range(first_weekday):
        days.append(None)
    
    # Add all days of the month
    for day in range(1, num_days + 1):
        days.append(date(year, month, day))
    
    return days

# Legacy views for backward compatibility
@login_required
def appointment_detail(request, appointment_id):
    """Legacy view - redirect to slot detail"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if hasattr(appointment, 'appointment_slot') and appointment.appointment_slot:
            return redirect('doctor:slot_detail', slot_id=appointment.appointment_slot.id)
        else:
            messages.error(request, 'Appointment slot not found.')
            return redirect('doctor:appointment_calendar')
    except:
        messages.error(request, 'Appointment not found.')
        return redirect('doctor:appointment_calendar')

@login_required
def create_appointment(request):
    """Legacy view - redirect to create slots"""
    return redirect('doctor:create_appointment_slots')

@login_required
def edit_appointment(request, appointment_id):
    """Legacy view - redirect to slot detail"""
    return redirect('doctor:appointment_detail', appointment_id=appointment_id)

@login_required
def delete_appointment(request, appointment_id):
    """Legacy view - redirect to slot detail"""
    return redirect('doctor:appointment_detail', appointment_id=appointment_id)

@login_required
def patient_search_api(request):
    """API endpoint for patient search"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            return JsonResponse({'error': 'Not authorized'}, status=403)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor profile not found'}, status=404)
    
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'patients': []})
    
    # Search patients by name or email
    patients = Patient.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__email__icontains=query),
        user__is_active=True
    ).select_related('user')[:10]
    
    patient_data = []
    for patient in patients:
        patient_data.append({
            'id': patient.id,
            'name': patient.user.get_full_name(),
            'email': patient.user.email,
            'display': f"{patient.user.get_full_name()} ({patient.user.email})"
        })
    
    return JsonResponse({'patients': patient_data}) 