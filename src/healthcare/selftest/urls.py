from django.urls import path
from . import views

app_name = 'selftest'

urlpatterns = [
    # Main pages
    path('', views.selftest_home, name='home'),
    path('dashboard/', views.selftest_dashboard, name='dashboard'),
    path('hello/', views.hello_world, name='hello'),
    
    # Quick test
    path('quick/', views.quick_test, name='quick_test'),
    path('results/<int:test_id>/', views.analysis_results, name='test_results'),
    
    # Test history
    path('history/', views.test_history, name='test_history'),
    
    # API endpoints
    path('api/quick-symptom-search/', views.quick_symptom_search_api, name='quick_symptom_search_api'),
] 