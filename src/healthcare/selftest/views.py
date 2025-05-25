from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from patient.models import Patient
from .models import SelfTest, Symptom, SymptomReport
from .forms import QuickTestForm
from .ai_engine import HealthAIEngine
import json


def selftest_home(request):
    """Self-test system homepage"""
    return render(request, 'selftest/home.html', {
        'title': 'AI-Powered Self-Test System',
        'message': 'Analyze your symptoms with our advanced AI health assessment tool'
    })


@login_required
def selftest_dashboard(request):
    """Patient self-test dashboard with history and analytics"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found. Please contact support.")
        return redirect('selftest:home')
    
    # Get recent self-tests
    recent_tests = SelfTest.objects.filter(patient=patient)[:5]
    
    # Calculate statistics
    total_tests = SelfTest.objects.filter(patient=patient).count()
    risk_distribution = {
        'low': SelfTest.objects.filter(patient=patient, risk_level='low').count(),
        'medium': SelfTest.objects.filter(patient=patient, risk_level='medium').count(),
        'high': SelfTest.objects.filter(patient=patient, risk_level='high').count(),
        'urgent': SelfTest.objects.filter(patient=patient, risk_level='urgent').count(),
    }
    
    context = {
        'title': 'Self-Test Dashboard',
        'patient': patient,
        'recent_tests': recent_tests,
        'total_tests': total_tests,
        'risk_distribution': risk_distribution,
    }
    
    return render(request, 'selftest/dashboard.html', context)





@login_required
def quick_test(request):
    """Quick symptom analysis with AJAX search"""
    if request.method == 'POST':
        # Get selected symptoms from AJAX form
        selected_symptoms_json = request.POST.get('selected_symptoms', '[]')
        additional_notes = request.POST.get('additional_notes', '')
        
        try:
            selected_symptoms = json.loads(selected_symptoms_json)
        except json.JSONDecodeError:
            selected_symptoms = []
        
        if not selected_symptoms:
            return JsonResponse({
                'success': False,
                'error': 'Please select at least one symptom.'
            })
        
        # Prepare symptom reports for AI analysis
        symptom_reports = []
        for symptom_data in selected_symptoms:
            symptom_reports.append({
                'symptom_name': symptom_data['name'],
                'severity': symptom_data['severity'],
                'duration_days': symptom_data.get('duration', 1)
            })
        
        # Analyze with AI
        ai_engine = HealthAIEngine()
        analysis_result = ai_engine.analyze_symptoms(symptom_reports)
        
        # Save to database
        try:
            patient = Patient.objects.get(user=request.user)
            self_test = SelfTest.objects.create(
                patient=patient,
                risk_level=analysis_result['risk_level'],
                ai_recommendation=analysis_result['recommendations'],
                predicted_diseases=analysis_result['predicted_diseases'],
                additional_notes=additional_notes
            )
            
            # Create symptom reports
            for symptom_data in selected_symptoms:
                # Get or create symptom
                symptom, created = Symptom.objects.get_or_create(
                    name=symptom_data['name'],
                    defaults={
                        'description': symptom_data.get('description', ''),
                        'category': symptom_data.get('category', 'General')
                    }
                )
                
                SymptomReport.objects.create(
                    self_test=self_test,
                    symptom=symptom,
                    severity=symptom_data['severity'],
                    duration_days=symptom_data.get('duration', 1),
                    notes=symptom_data.get('notes', '')
                )
            
            return JsonResponse({
                'success': True,
                'redirect_url': f'/selftest/results/{self_test.id}/'
            })
            
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Patient profile not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error saving test: {str(e)}'
            })
    
    # GET request - show quick test form
    ai_engine = HealthAIEngine()
    initial_symptoms = ai_engine.search_symptoms("", limit=10)
    
    context = {
        'title': 'Quick Health Assessment',
        'symptoms': initial_symptoms,
    }
    
    return render(request, 'selftest/quick_test.html', context)


@login_required
def quick_symptom_search_api(request):
    """API endpoint for quick test symptom search"""
    query = request.GET.get('q', '')
    ai_engine = HealthAIEngine()
    
    symptoms = ai_engine.search_symptoms(query, limit=10)
    
    return JsonResponse({
        'success': True,
        'symptoms': symptoms,
        'count': len(symptoms)
    })


@login_required
def analysis_results(request, test_id):
    """Display AI analysis results for a specific test"""
    try:
        patient = Patient.objects.get(user=request.user)
        self_test = get_object_or_404(SelfTest, id=test_id, patient=patient)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('selftest:home')
    
    # Get symptom reports for display
    symptom_reports = self_test.symptom_reports.all()
    
    context = {
        'title': 'Health Analysis Results',
        'self_test': self_test,
        'symptom_reports': symptom_reports,
        'predicted_diseases': self_test.predicted_diseases,
        'risk_level': self_test.risk_level,
        'recommendations': self_test.ai_recommendation,
    }
    
    return render(request, 'selftest/results.html', context)


@login_required
def test_history(request):
    """View test history with filtering and pagination"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('selftest:home')
    
    # Get all tests for this patient
    tests = SelfTest.objects.filter(patient=patient)
    
    # Filter by risk level if specified
    risk_filter = request.GET.get('risk')
    if risk_filter and risk_filter in ['low', 'medium', 'high', 'urgent']:
        tests = tests.filter(risk_level=risk_filter)
    
    # Pagination
    paginator = Paginator(tests, 10)  # 10 tests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Test History',
        'page_obj': page_obj,
        'risk_filter': risk_filter,
    }
    
    return render(request, 'selftest/history.html', context)


def hello_world(request):
    """Simple hello world view for testing"""
    return HttpResponse(
        "<h1>Hello World from Self-Test App!</h1>"
        "<p>AI-Powered Health Assessment System is now active!</p>"
        "<p><a href='/selftest/'>Go to Self-Test Home</a></p>"
    )
