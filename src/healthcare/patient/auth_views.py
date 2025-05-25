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