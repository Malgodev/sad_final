"""
URL configuration for healthcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Healthcare System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); min-height: 100vh; }
            .card { border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
            .btn-custom { border-radius: 8px; padding: 12px 20px; margin: 5px; }
            .doctor-link { position: absolute; top: 20px; right: 20px; color: white; text-decoration: none; opacity: 0.8; }
            .doctor-link:hover { opacity: 1; color: white; }
        </style>
    </head>
    <body>
        <a href="/doctor/auth/" class="doctor-link">
            <i class="fas fa-user-md"></i> Doctor Login
        </a>
        
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center p-5">
                            <h1 class="mb-4"><i class="fas fa-heartbeat text-danger"></i> Healthcare System</h1>
                            <p class="lead mb-4">Welcome to our Patient Portal!</p>
                            
                            <div class="mb-4">
                                <h4><i class="fas fa-user-injured text-danger"></i> Patient Access</h4>
                                <a href="/patient/login/" class="btn btn-danger btn-custom w-100 mb-2">
                                    <i class="fas fa-sign-in-alt"></i> Patient Login
                                </a>
                                <a href="/patient/register/" class="btn btn-outline-danger btn-custom w-100 mb-3">
                                    <i class="fas fa-user-plus"></i> Patient Registration
                                </a>
                            </div>
                            
                            <hr>
                            
                            <h5>Patient Services</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <a href="/patient/" class="btn btn-light btn-custom w-100 mb-2">
                                        <i class="fas fa-user-injured"></i><br>Patient Portal
                                    </a>
                                </div>
                                <div class="col-md-6">
                                    <a href="/appointment/" class="btn btn-light btn-custom w-100 mb-2">
                                        <i class="fas fa-calendar-check"></i><br>Appointments
                                    </a>
                                </div>
                                <div class="col-md-6">
                                    <a href="/selftest/" class="btn btn-light btn-custom w-100">
                                        <i class="fas fa-stethoscope"></i><br>Self Test
                                    </a>
                                </div>
                                <div class="col-md-6">
                                    <a href="/admin/" class="btn btn-secondary btn-custom w-100">
                                        <i class="fas fa-cog"></i><br>Admin Panel
                                    </a>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle"></i> 
                                    Medical professionals can access the doctor portal using the link in the top-right corner.
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('doctor/', include('doctor.urls')),
    path('patient/', include('patient.urls')),
    path('appointment/', include('appointment.urls')),
    path('selftest/', include('selftest.urls')),
]
