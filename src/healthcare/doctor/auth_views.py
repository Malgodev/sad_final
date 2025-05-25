from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import DoctorRegistrationForm, DoctorLoginForm
from .models import Doctor
import json

class DoctorRegistrationView(View):
    def get(self, request):
        form = DoctorRegistrationForm()
        return render(request, 'doctor/register.html', {
            'form': form,
            'user_type': 'Doctor',
            'login_url': '/doctor/auth/',
            'title': 'Doctor Registration'
        })

    def post(self, request):
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Doctor account created successfully! Your account is pending admin approval. You will be notified once approved.')
            return redirect('doctor:auth_login')
        return render(request, 'doctor/register.html', {
            'form': form,
            'user_type': 'Doctor',
            'login_url': '/doctor/auth/',
            'title': 'Doctor Registration'
        })

class DoctorLoginView(View):
    def get(self, request):
        form = DoctorLoginForm()
        return render(request, 'doctor/login.html', {
            'form': form,
            'user_type': 'Doctor',
            'register_url': '/doctor/auth/register/',
            'title': 'Doctor Login'
        })

    def post(self, request):
        form = DoctorLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is a doctor
                try:
                    doctor = Doctor.objects.get(user=user)
                    
                    # Check approval status
                    if doctor.approval_status == 'pending':
                        messages.warning(request, 'Your doctor account is pending admin approval. Please wait for approval before logging in.')
                    elif doctor.approval_status == 'rejected':
                        messages.error(request, 'Your doctor account has been rejected. Please contact administration for more information.')
                    elif doctor.approval_status == 'approved':
                        login(request, user)
                        
                        # Generate JWT tokens
                        refresh = RefreshToken.for_user(user)
                        access_token = refresh.access_token
                        
                        # Store tokens in session for web interface
                        request.session['access_token'] = str(access_token)
                        request.session['refresh_token'] = str(refresh)
                        
                        messages.success(request, f'Welcome back, Dr. {user.first_name}!')
                        return redirect('doctor:dashboard')
                    else:
                        messages.error(request, 'Your account status is unknown. Please contact administration.')
                except Doctor.DoesNotExist:
                    messages.error(request, 'This account is not registered as a doctor.')
            else:
                messages.error(request, 'Invalid username or password.')
        
        return render(request, 'doctor/login.html', {
            'form': form,
            'user_type': 'Doctor',
            'register_url': '/doctor/auth/register/',
            'title': 'Doctor Login'
        })

@method_decorator(csrf_exempt, name='dispatch')
class DoctorAPILoginView(View):
    """API endpoint for doctor login that returns JWT tokens"""
    
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
                    doctor = Doctor.objects.get(user=user)
                    
                    # Check approval status
                    if doctor.approval_status != 'approved':
                        status_messages = {
                            'pending': 'Your doctor account is pending admin approval',
                            'rejected': 'Your doctor account has been rejected'
                        }
                        return JsonResponse({
                            'error': status_messages.get(doctor.approval_status, 'Account not approved')
                        }, status=403)
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    return JsonResponse({
                        'access_token': str(access_token),
                        'refresh_token': str(refresh),
                        'user_type': 'doctor',
                        'user_id': user.id,
                        'doctor_id': doctor.id,
                        'name': f"Dr. {user.first_name} {user.last_name}",
                        'specialization': doctor.specialization,
                        'approval_status': doctor.approval_status
                    })
                except Doctor.DoesNotExist:
                    return JsonResponse({
                        'error': 'This account is not registered as a doctor'
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

def doctor_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('doctor:auth_login') 