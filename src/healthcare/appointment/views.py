from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Appointment

def appointment_home(request):
    return HttpResponse("""
    <h1>Appointment System - Hello World</h1>
    <p>Welcome to the Appointment Management System!</p>
    <ul>
        <li><a href="/appointment/list/">View All Appointments</a></li>
        <li><a href="/appointment/book/">Book New Appointment</a></li>
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
