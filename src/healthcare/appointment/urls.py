from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.appointment_home, name='home'),
    path('list/', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
] 