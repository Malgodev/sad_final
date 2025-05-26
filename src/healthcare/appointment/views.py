from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Appointment
from .chatbot import AppointmentChatbot

def appointment_home(request):
    return HttpResponse("""
    <h1>Appointment System - Hello World</h1>
    <p>Welcome to the Appointment Management System!</p>
    <ul>
        <li><a href="/appointment/list/">View All Appointments</a></li>
        <li><a href="/appointment/book/">Book New Appointment</a></li>
        <li><a href="/appointment/chatbot/">AI Appointment Assistant</a></li>
        <li><a href="/">Back to Home</a></li>
    </ul>
    """)

def appointment_list(request):
    appointments = Appointment.objects.all()[:10]  # Show latest 10 appointments
    
    appointment_html = ""
    for apt in appointments:
        appointment_html += f"""
        <li>
            {apt.patient.user.get_full_name()} with Dr. {apt.doctor.user.get_full_name()}<br>
            Date: {apt.appointment_date.strftime('%Y-%m-%d %H:%M')}<br>
            Status: {apt.get_status_display()}<br>
            Reason: {apt.reason or 'Not specified'}
        </li><br>
        """
    
    if not appointment_html:
        appointment_html = "<li>No appointments found.</li>"
    
    return HttpResponse(f"""
    <h1>All Appointments</h1>
    <ul>
        {appointment_html}
    </ul>
    <a href="/appointment/">Back to Appointment System</a>
    """)

def book_appointment(request):
    return HttpResponse("""
    <h1>Book New Appointment</h1>
    <p>Appointment booking form coming soon...</p>
    <p>This will include:</p>
    <ul>
        <li>Doctor selection</li>
        <li>Date and time picker</li>
        <li>Reason for visit</li>
        <li>Patient information</li>
    </ul>
    <a href="/appointment/">Back to Appointment System</a>
    """)

@login_required
def appointment_chatbot(request):
    """Main chatbot interface for appointment recommendations"""
    try:
        from patient.models import Patient
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return render(request, 'appointment/chatbot_error.html', {
            'error': 'Patient profile not found. Please complete your profile first.'
        })
    
    chatbot = AppointmentChatbot()
    quick_suggestions = chatbot.get_quick_suggestions()
    
    context = {
        'patient': patient,
        'quick_suggestions': quick_suggestions,
    }
    
    return render(request, 'appointment/chatbot.html', context)

@login_required
@require_http_methods(["POST"])
def chatbot_analyze(request):
    """API endpoint for chatbot analysis"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        criteria = data.get('criteria', {})
        
        if not user_message:
            return JsonResponse({
                'error': 'Please provide a message describing your condition or symptoms.'
            }, status=400)
        
        # Initialize chatbot and analyze
        chatbot = AppointmentChatbot()
        result = chatbot.analyze_user_input(user_message, criteria)
        
        return JsonResponse({
            'success': True,
            'response': result['message'],
            'doctors': result['recommended_doctors'],
            'specializations': result['specializations'],
            'confidence': result['confidence']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data provided.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
def chatbot_suggestions(request):
    """API endpoint for quick suggestions"""
    chatbot = AppointmentChatbot()
    suggestions = chatbot.get_quick_suggestions()
    
    return JsonResponse({
        'suggestions': suggestions
    })

@login_required
def specialization_info(request, specialization):
    """API endpoint for specialization information"""
    chatbot = AppointmentChatbot()
    info = chatbot.get_specialization_info(specialization)
    
    return JsonResponse({
        'specialization': specialization,
        'info': info
    })

@login_required
def doctor_availability(request, doctor_id):
    """API endpoint to check doctor availability"""
    try:
        from doctor.models import Doctor
        from appointment.models import AppointmentSlot
        from datetime import date, timedelta
        
        doctor = Doctor.objects.get(id=doctor_id, approval_status='approved')
        
        # Get available slots for the next 30 days
        today = date.today()
        end_date = today + timedelta(days=30)
        
        available_slots = AppointmentSlot.objects.filter(
            doctor=doctor,
            date__range=[today, end_date],
            appointment__isnull=True
        ).order_by('date', 'slot_type')[:20]
        
        slots_data = []
        for slot in available_slots:
            slots_data.append({
                'id': slot.id,
                'date': slot.date.strftime('%Y-%m-%d'),
                'slot_type': slot.slot_type,
                'slot_display': slot.get_slot_type_display(),
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M')
            })
        
        return JsonResponse({
            'doctor': {
                'id': doctor.id,
                'name': doctor.user.get_full_name(),
                'specialization': doctor.specialization,
                'experience_years': doctor.experience_years,
                'phone': doctor.phone
            },
            'available_slots': slots_data
        })
        
    except Doctor.DoesNotExist:
        return JsonResponse({
            'error': 'Doctor not found or not approved.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
def specialization_doctors_links(request, specialization):
    """API endpoint to get direct links to doctors by specialization"""
    try:
        from doctor.models import Doctor
        
        doctors = Doctor.objects.filter(
            specialization__icontains=specialization,
            approval_status='approved'
        ).select_related('user').order_by('-experience_years')[:5]
        
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'name': doctor.user.get_full_name(),
                'specialization': doctor.specialization,
                'experience_years': doctor.experience_years,
                'profile_link': f'/doctor/profile/{doctor.id}/',
                'booking_link': f'/patient/appointments/calendar/?doctor={doctor.id}',
                'phone': doctor.phone
            })
        
        return JsonResponse({
            'specialization': specialization,
            'doctors': doctors_data,
            'links_message': f"Here are direct links to {specialization} specialists:\n\n" + 
                           "\n".join([
                               f"🔗 Dr. {doc['name']} - {doc['experience_years']} years\n"
                               f"📋 Profile: {doc['profile_link']}\n"
                               f"📅 Book: {doc['booking_link']}\n"
                               for doc in doctors_data
                           ])
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)
