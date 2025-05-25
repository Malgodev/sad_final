from django.urls import path
from . import views
from .auth_views import DoctorRegistrationView, DoctorLoginView, DoctorAPILoginView, doctor_logout
from . import appointment_views

app_name = 'doctor'

urlpatterns = [
    path('', views.doctor_home, name='home'),
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('profile/', views.doctor_profile, name='profile'),
    
    # Doctor Authentication URLs (separate from patient login)
    path('auth/', DoctorLoginView.as_view(), name='auth_login'),
    path('auth/register/', DoctorRegistrationView.as_view(), name='auth_register'),
    path('auth/logout/', doctor_logout, name='auth_logout'),
    
    # Appointment Slot Management URLs
    path('appointments/', appointment_views.appointment_calendar, name='appointment_calendar'),
    path('appointments/list/', appointment_views.appointment_list, name='appointment_list'),
    path('appointments/create-slots/', appointment_views.create_appointment_slots, name='create_appointment_slots'),
    path('appointments/bulk-create/', appointment_views.bulk_create_slots, name='bulk_create_slots'),
    path('appointments/slot/<int:slot_id>/', appointment_views.slot_detail, name='slot_detail'),
    path('appointments/slot/<int:slot_id>/delete/', appointment_views.delete_slot, name='delete_slot'),
    
    # Legacy appointment URLs (for backward compatibility)
    path('appointments/create/', appointment_views.create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/', appointment_views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/edit/', appointment_views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:appointment_id>/delete/', appointment_views.delete_appointment, name='delete_appointment'),
    
    # API Endpoints
    path('api/login/', DoctorAPILoginView.as_view(), name='api_login'),
    path('api/patients/search/', appointment_views.patient_search_api, name='patient_search_api'),
] 