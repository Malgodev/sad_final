# Appointment App Documentation - Part 2

## 5. Views (views.py)

```python
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
```

## 6. AI Chatbot System (chatbot.py)

### a. Main Chatbot Class

```python
import json
import os
from typing import List, Dict, Tuple
from django.conf import settings
from doctor.models import Doctor
from django.db.models import Q


class AppointmentChatbot:
    """AI Chatbot for appointment recommendations based on diseases and criteria"""
    
    def __init__(self):
        self.disease_specialization_map = self._load_disease_specialization_mapping()
        self.specialization_keywords = self._load_specialization_keywords()
    
    def _load_disease_specialization_mapping(self) -> Dict:
        """Load disease to specialization mapping"""
        return {
            # Cardiovascular diseases
            "heart disease": ["Cardiology", "Internal Medicine"],
            "chest pain": ["Cardiology", "Emergency Medicine", "Internal Medicine"],
            "high blood pressure": ["Cardiology", "Internal Medicine", "Family Medicine"],
            "heart attack": ["Cardiology", "Emergency Medicine"],
            "arrhythmia": ["Cardiology"],
            "heart failure": ["Cardiology", "Internal Medicine"],
            
            # Respiratory diseases
            "asthma": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "pneumonia": ["Pulmonology", "Internal Medicine", "Emergency Medicine"],
            "bronchitis": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "cough": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "shortness of breath": ["Pulmonology", "Cardiology", "Internal Medicine"],
            "lung disease": ["Pulmonology"],
            
            # Gastrointestinal diseases
            "stomach pain": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "nausea": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "diarrhea": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "constipation": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "acid reflux": ["Gastroenterology", "Internal Medicine"],
            "ulcer": ["Gastroenterology", "Internal Medicine"],
            
            # Neurological diseases
            "headache": ["Neurology", "Internal Medicine", "Family Medicine"],
            "migraine": ["Neurology", "Internal Medicine"],
            "seizure": ["Neurology", "Emergency Medicine"],
            "stroke": ["Neurology", "Emergency Medicine"],
            "memory loss": ["Neurology", "Geriatrics"],
            "dizziness": ["Neurology", "Internal Medicine", "ENT"],
            
            # Orthopedic conditions
            "back pain": ["Orthopedics", "Physical Medicine", "Family Medicine"],
            "joint pain": ["Orthopedics", "Rheumatology", "Internal Medicine"],
            "fracture": ["Orthopedics", "Emergency Medicine"],
            "arthritis": ["Rheumatology", "Orthopedics", "Internal Medicine"],
            "muscle pain": ["Orthopedics", "Physical Medicine", "Family Medicine"],
            
            # Dermatological conditions
            "skin rash": ["Dermatology", "Family Medicine", "Internal Medicine"],
            "acne": ["Dermatology", "Family Medicine"],
            "eczema": ["Dermatology", "Allergy and Immunology"],
            "psoriasis": ["Dermatology"],
            "skin cancer": ["Dermatology", "Oncology"],
            
            # Endocrine disorders
            "diabetes": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            "thyroid": ["Endocrinology", "Internal Medicine"],
            "weight loss": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            "weight gain": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            
            # Mental health
            "depression": ["Psychiatry", "Psychology", "Family Medicine"],
            "anxiety": ["Psychiatry", "Psychology", "Family Medicine"],
            "stress": ["Psychiatry", "Psychology", "Family Medicine"],
            "insomnia": ["Psychiatry", "Sleep Medicine", "Internal Medicine"],
            
            # Women's health
            "pregnancy": ["Obstetrics and Gynecology", "Family Medicine"],
            "menstrual": ["Obstetrics and Gynecology", "Family Medicine"],
            "pelvic pain": ["Obstetrics and Gynecology", "Internal Medicine"],
            
            # General symptoms
            "fever": ["Internal Medicine", "Family Medicine", "Emergency Medicine"],
            "fatigue": ["Internal Medicine", "Family Medicine"],
            "weight loss": ["Internal Medicine", "Oncology", "Endocrinology"],
            "pain": ["Internal Medicine", "Family Medicine", "Pain Management"],
            "infection": ["Internal Medicine", "Family Medicine", "Infectious Disease"],
            
            # Emergency conditions
            "emergency": ["Emergency Medicine"],
            "trauma": ["Emergency Medicine", "Surgery"],
            "accident": ["Emergency Medicine", "Surgery", "Orthopedics"],
        }
    
    def _load_specialization_keywords(self) -> Dict:
        """Load keywords for each specialization"""
        return {
            "Cardiology": ["heart", "cardiac", "cardiovascular", "chest pain", "blood pressure", "arrhythmia"],
            "Pulmonology": ["lung", "respiratory", "breathing", "cough", "asthma", "pneumonia"],
            "Gastroenterology": ["stomach", "digestive", "intestinal", "bowel", "liver", "gallbladder"],
            "Neurology": ["brain", "neurological", "headache", "seizure", "stroke", "memory"],
            "Orthopedics": ["bone", "joint", "muscle", "fracture", "spine", "back pain"],
            "Dermatology": ["skin", "rash", "acne", "eczema", "mole", "dermatitis"],
            "Endocrinology": ["diabetes", "thyroid", "hormone", "metabolism", "weight"],
            "Psychiatry": ["mental", "depression", "anxiety", "stress", "mood", "psychiatric"],
            "Obstetrics and Gynecology": ["women", "pregnancy", "gynecological", "menstrual", "reproductive"],
            "Emergency Medicine": ["emergency", "urgent", "trauma", "accident", "critical"],
            "Internal Medicine": ["general", "internal", "primary care", "chronic", "medical"],
            "Family Medicine": ["family", "primary", "general practice", "preventive"],
            "Pediatrics": ["children", "pediatric", "infant", "child", "adolescent"],
            "Surgery": ["surgical", "operation", "procedure", "tumor", "mass"],
            "Oncology": ["cancer", "tumor", "oncology", "chemotherapy", "radiation"],
            "Rheumatology": ["arthritis", "autoimmune", "joint inflammation", "lupus"],
            "Urology": ["kidney", "bladder", "urinary", "prostate", "urological"],
            "ENT": ["ear", "nose", "throat", "sinus", "hearing", "voice"],
            "Ophthalmology": ["eye", "vision", "sight", "retina", "glaucoma"],
            "Anesthesiology": ["anesthesia", "pain management", "surgical anesthesia"],
        }
    
    def analyze_user_input(self, user_message: str, criteria: Dict = None) -> Dict:
        """
        Analyze user input and recommend doctors
        
        Args:
            user_message: User's description of disease/symptoms
            criteria: Additional criteria like location, experience, etc.
        
        Returns:
            Dict with recommended doctors and analysis
        """
        user_message_lower = user_message.lower()
        
        # Find matching specializations
        recommended_specializations = self._find_specializations(user_message_lower)
        
        # Get available doctors
        recommended_doctors = self._get_recommended_doctors(
            recommended_specializations, 
            criteria or {}
        )
        
        # Generate response message
        response_message = self._generate_response_message(
            user_message, 
            recommended_specializations, 
            recommended_doctors
        )
        
        return {
            'message': response_message,
            'recommended_doctors': recommended_doctors,
            'specializations': recommended_specializations,
            'confidence': self._calculate_confidence(user_message_lower, recommended_specializations)
        }
    
    def _find_specializations(self, user_input: str) -> List[Dict]:
        """Find matching specializations based on user input"""
        specialization_scores = {}
        
        # Check disease mapping
        for disease, specializations in self.disease_specialization_map.items():
            if disease in user_input:
                for spec in specializations:
                    specialization_scores[spec] = specialization_scores.get(spec, 0) + 3
        
        # Check keyword mapping
        for specialization, keywords in self.specialization_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    specialization_scores[specialization] = specialization_scores.get(specialization, 0) + 1
        
        # Sort by score and return top specializations
        sorted_specs = sorted(specialization_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'name': spec,
                'score': score,
                'relevance': min(score * 20, 100)  # Convert to percentage
            }
            for spec, score in sorted_specs[:5]
        ]
    
    def _get_recommended_doctors(self, specializations: List[Dict], criteria: Dict) -> List[Dict]:
        """Get recommended doctors based on specializations and criteria"""
        if not specializations:
            # If no specific specialization found, recommend general practitioners
            specializations = [{'name': 'Internal Medicine'}, {'name': 'Family Medicine'}]
        
        # Build query
        spec_names = [spec['name'] for spec in specializations]
        query = Q(specialization__in=spec_names) & Q(approval_status='approved')
        
        # Apply additional criteria
        if criteria.get('min_experience'):
            query &= Q(experience_years__gte=criteria['min_experience'])
        
        # Get doctors
        doctors = Doctor.objects.filter(query).select_related('user').order_by('-experience_years')[:10]
        
        recommended_doctors = []
        for doctor in doctors:
            # Calculate relevance score
            relevance = 50  # Base score
            for spec in specializations:
                if spec['name'] == doctor.specialization:
                    relevance += spec.get('relevance', 50)
                    break
            
            # Experience bonus
            if doctor.experience_years > 10:
                relevance += 20
            elif doctor.experience_years > 5:
                relevance += 10
            
            relevance = min(relevance, 100)
            
            recommended_doctors.append({
                'id': doctor.id,
                'name': doctor.user.get_full_name(),
                'specialization': doctor.specialization,
                'experience_years': doctor.experience_years,
                'phone': doctor.phone,
                'license_number': doctor.license_number,
                'relevance_score': relevance
            })
        
        # Sort by relevance score
        recommended_doctors.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommended_doctors
    
    def _generate_response_message(self, user_input: str, specializations: List[Dict], doctors: List[Dict]) -> str:
        """Generate chatbot response message"""
        if not doctors:
            return """I understand you're looking for medical assistance, but I couldn't find specific doctors for your condition. 
            I recommend consulting with a General Medicine or Family Medicine doctor who can evaluate your symptoms and refer you to the appropriate specialist if needed."""
        
        response_parts = []
        
        # Greeting and understanding
        response_parts.append(f"I understand you're experiencing: '{user_input}'")
        
        # Specialization recommendation
        if specializations:
            top_spec = specializations[0]
            response_parts.append(f"Based on your description, I recommend consulting with a {top_spec['name']} specialist.")
        
        # Doctor recommendations with direct links
        if len(doctors) == 1:
            doctor = doctors[0]
            response_parts.append(f"I found an excellent doctor for you:")
            response_parts.append(f"🔗 Dr. {doctor['name']} ({doctor['specialization']}) - {doctor['experience_years']} years experience")
            response_parts.append(f"📋 View full profile: /doctor/profile/{doctor['id']}/")
            response_parts.append(f"📅 Book appointment: /patient/appointments/calendar/?doctor={doctor['id']}")
        else:
            response_parts.append(f"I found {len(doctors)} qualified doctors who can help you:")
            for i, doctor in enumerate(doctors[:3], 1):
                response_parts.append(f"\n{i}. 🔗 Dr. {doctor['name']} - {doctor['specialization']} ({doctor['experience_years']} years)")
                response_parts.append(f"   📋 Profile: /doctor/profile/{doctor['id']}/")
                response_parts.append(f"   📅 Book: /patient/appointments/calendar/?doctor={doctor['id']}")
        
        # Next steps
        response_parts.append("\n💡 Click the links above to view doctor profiles and book appointments directly!")
        response_parts.append("You can also use the 'Profile' and 'Book Now' buttons in the doctor cards below.")
        
        return "\n".join(response_parts)
    
    def _calculate_confidence(self, user_input: str, specializations: List[Dict]) -> int:
        """Calculate confidence score for the recommendation"""
        if not specializations:
            return 30
        
        # Base confidence on number of matching keywords/diseases
        confidence = min(specializations[0].get('relevance', 50), 90)
        
        # Boost confidence for specific disease mentions
        for disease in self.disease_specialization_map.keys():
            if disease in user_input:
                confidence = min(confidence + 20, 95)
                break
        
        return max(confidence, 40)  # Minimum 40% confidence
    
    def get_quick_suggestions(self) -> List[str]:
        """Get quick suggestion prompts for users"""
        return [
            "I have chest pain and shortness of breath",
            "I'm experiencing severe headaches",
            "I have stomach pain and nausea",
            "I need help with diabetes management",
            "I have back pain that won't go away",
            "I'm feeling anxious and depressed",
            "I have a skin rash that's spreading",
            "I need a general health checkup",
            "I'm pregnant and need prenatal care",
            "I have joint pain and stiffness"
        ]
    
    def get_specialization_info(self, specialization: str) -> Dict:
        """Get information about a specific specialization"""
        info_map = {
            "Cardiology": {
                "description": "Heart and cardiovascular system specialists",
                "treats": ["Heart disease", "High blood pressure", "Chest pain", "Arrhythmia"],
                "when_to_see": "Chest pain, heart palpitations, high blood pressure"
            },
            "Pulmonology": {
                "description": "Lung and respiratory system specialists",
                "treats": ["Asthma", "Pneumonia", "Bronchitis", "Lung disease"],
                "when_to_see": "Persistent cough, breathing difficulties, chest congestion"
            },
            "Gastroenterology": {
                "description": "Digestive system specialists",
                "treats": ["Stomach pain", "Acid reflux", "Ulcers", "Liver disease"],
                "when_to_see": "Stomach pain, digestive issues, bowel problems"
            },
            "Neurology": {
                "description": "Brain and nervous system specialists",
                "treats": ["Headaches", "Seizures", "Stroke", "Memory problems"],
                "when_to_see": "Severe headaches, neurological symptoms, memory issues"
            },
            "Internal Medicine": {
                "description": "General adult medicine specialists",
                "treats": ["General health", "Chronic diseases", "Preventive care"],
                "when_to_see": "General health concerns, routine checkups, chronic conditions"
            }
        }
        
        return info_map.get(specialization, {
            "description": f"{specialization} specialist",
            "treats": ["Various conditions in this specialty"],
            "when_to_see": "Conditions related to this medical specialty"
        })
```

## 7. Database Migrations

### a. Initial Migration (migrations/0001_initial.py)

```python
# Generated by Django 4.2.21 on 2025-05-25 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctor', '0001_initial'),
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateTimeField()),
                ('duration_minutes', models.IntegerField(default=30)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('no_show', 'No Show')], default='scheduled', max_length=20)),
                ('reason', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='doctor.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patient.patient')),
            ],
            options={
                'verbose_name': 'Appointment',
                'verbose_name_plural': 'Appointments',
                'ordering': ['-appointment_date'],
            },
        ),
    ]
```

### b. Slot System Migration (migrations/0002_alter_appointment_duration_minutes_and_more.py)

```python
# Generated by Django 4.2.21 on 2025-05-25 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_doctor_approval_status_doctor_approved_at_and_more'),
        ('patient', '0001_initial'),
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='duration_minutes',
            field=models.IntegerField(default=90),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patient.patient'),
        ),
        migrations.CreateModel(
            name='AppointmentSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('slot_type', models.CharField(choices=[('morning_1', 'Morning 8:00 - 9:30'), ('morning_2', 'Morning 10:00 - 11:30'), ('afternoon_1', 'Afternoon 1:30 - 3:00'), ('afternoon_2', 'Afternoon 3:30 - 5:00')], max_length=20)),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_slots', to='doctor.doctor')),
            ],
            options={
                'verbose_name': 'Appointment Slot',
                'verbose_name_plural': 'Appointment Slots',
                'ordering': ['date', 'slot_type'],
                'unique_together': {('doctor', 'date', 'slot_type')},
            },
        ),
        migrations.AddField(
            model_name='appointment',
            name='appointment_slot',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment', to='appointment.appointmentslot'),
        ),
    ]
```

## 8. Tests (tests.py)

```python
from django.test import TestCase

# Create your tests here.
```

## 9. Key Features Summary

### a. Appointment Slot System
- **Four predefined time slots** (Morning 8:00-9:30, 10:00-11:30, Afternoon 1:30-3:00, 3:30-5:00)
- **Doctor-created availability** with date and slot type combinations
- **Unique constraint** preventing duplicate slots
- **Property methods** for start/end times and datetime objects

### b. AI-Powered Chatbot
- **Disease-to-specialization mapping** with over 50 conditions
- **Keyword-based specialization matching** for intelligent recommendations
- **Confidence scoring system** based on symptom relevance
- **Direct booking links** in chatbot responses
- **Quick suggestion prompts** for common medical conditions

### c. Doctor Recommendation Engine
- **Relevance scoring** based on specialization match and experience
- **Multi-criteria filtering** including experience years
- **Automatic fallback** to general practitioners when no specific match found
- **API endpoints** for real-time doctor availability checks

### d. Appointment Management
- **Status tracking** (scheduled, confirmed, completed, cancelled, no_show)
- **Patient-doctor relationships** with optional patient field for available slots
- **90-minute fixed duration** slots for consistent scheduling
- **Notes and reason fields** for appointment details

### e. Form Validation & UI
- **Date validation** preventing past date appointments
- **Bulk slot creation** with date range and weekday selection
- **Responsive form widgets** with Bootstrap styling
- **Appointment status update forms** for doctors

### f. Admin Interface
- **Comprehensive filtering** by status, date, specialization
- **Search functionality** across patient and doctor names
- **Date hierarchy** for easy navigation
- **Boolean indicators** for slot booking status

This appointment app provides a complete solution for healthcare appointment management with AI-powered doctor recommendations, flexible slot creation, and comprehensive booking tracking capabilities. 