from django.urls import path
from . import views
from .auth_views import PatientRegistrationView, PatientLoginView, PatientAPILoginView, patient_logout
from . import appointment_views

app_name = 'patient'

urlpatterns = [
    path('', views.patient_home, name='home'),
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('profile/', views.patient_profile, name='profile'),
    path('appointments/', views.patient_appointments, name='appointments'),
    
    # Appointment Management URLs
    path('appointments/calendar/', appointment_views.patient_appointment_calendar, name='appointment_calendar'),
    path('appointments/list/', appointment_views.patient_appointment_list, name='appointment_list'),
    path('appointments/book/<int:slot_id>/', appointment_views.book_appointment, name='book_appointment'),
    path('appointments/detail/<int:appointment_id>/', appointment_views.appointment_detail, name='appointment_detail'),
    path('appointments/cancel/<int:appointment_id>/', appointment_views.cancel_appointment, name='cancel_appointment'),
    path('appointments/dashboard/', appointment_views.patient_dashboard_appointments, name='appointment_dashboard'),
    
    # API endpoints
    path('api/available-slots/', appointment_views.available_slots_api, name='available_slots_api'),
    
    # Authentication URLs
    path('register/', PatientRegistrationView.as_view(), name='register'),
    path('login/', PatientLoginView.as_view(), name='login'),
    path('logout/', patient_logout, name='logout'),
    
    # API Authentication
    path('api/login/', PatientAPILoginView.as_view(), name='api_login'),
] 