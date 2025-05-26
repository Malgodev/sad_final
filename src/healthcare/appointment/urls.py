from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.appointment_home, name='home'),
    path('list/', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
    
    # Chatbot URLs
    path('chatbot/', views.appointment_chatbot, name='chatbot'),
    path('api/chatbot/analyze/', views.chatbot_analyze, name='chatbot_analyze'),
    path('api/chatbot/suggestions/', views.chatbot_suggestions, name='chatbot_suggestions'),
    path('api/specialization/<str:specialization>/', views.specialization_info, name='specialization_info'),
    path('api/specialization/<str:specialization>/doctors/', views.specialization_doctors_links, name='specialization_doctors_links'),
    path('api/doctor/<int:doctor_id>/availability/', views.doctor_availability, name='doctor_availability'),
] 