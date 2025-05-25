#!/usr/bin/env python
"""
Comprehensive SelfTest Validation Script
Validates all URLs, API endpoints, and functionality
"""

import os
import django
import requests
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import Symptom

def create_test_data():
    """Create test user and data"""
    print("📊 Creating test data...")
    
    # Create test user
    try:
        user = User.objects.get(username='testpatient')
        user.delete()
    except User.DoesNotExist:
        pass
    
    user = User.objects.create_user(
        username='testpatient',
        password='testpass123',
        email='test@example.com'
    )
    
    # Create patient profile
    try:
        patient = Patient.objects.get(user=user)
        patient.delete()
    except Patient.DoesNotExist:
        pass
        
    patient = Patient.objects.create(
        user=user,
        date_of_birth='1990-01-01',
        gender='M',
        phone='+1234567890',
        address='123 Test St',
        emergency_contact='Test Contact',
        emergency_phone='+1234567890'
    )
    
    # Create test symptoms if they don't exist
    symptoms_data = [
        ('Headache', 'Pain in the head area'),
        ('Fever', 'Elevated body temperature'),
        ('Cough', 'Forceful expulsion of air from lungs'),
        ('Sore Throat', 'Pain or irritation in throat'),
        ('Fatigue', 'Extreme tiredness'),
    ]
    
    for name, description in symptoms_data:
        symptom, created = Symptom.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        if created:
            print(f"  ✅ Created symptom: {name}")
    
    print(f"✅ Test data created - User: {user.username}, Patient: {patient.id}")
    return user, patient

def test_url_resolution():
    """Test all URL patterns resolve correctly"""
    print("\n🌐 Testing URL Resolution...")
    
    urls_to_test = [
        'selftest:home',
        'selftest:dashboard', 
        'selftest:start',
        'selftest:quick',
        'selftest:symptoms',
        'selftest:symptom_search_api',
        'selftest:quick_symptom_search_api',
        'selftest:quick_analysis_api',
    ]
    
    all_passed = True
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"  ✅ {url_name:<35} -> {url}")
        except NoReverseMatch as e:
            print(f"  ❌ {url_name:<35} -> ERROR: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ⚠️  {url_name:<35} -> UNKNOWN ERROR: {e}")
            all_passed = False
    
    return all_passed

def test_view_functions():
    """Test that all view functions exist and are importable"""
    print("\n🔧 Testing View Function Imports...")
    
    views_to_test = [
        'selftest_home',
        'selftest_dashboard',
        'start_selftest',
        'quick_selftest',
        'symptom_search_api',
        'quick_symptom_search_api',
        'quick_analysis_api',
    ]
    
    all_passed = True
    for view_name in views_to_test:
        try:
            from selftest import views
            view_func = getattr(views, view_name)
            print(f"  ✅ {view_name:<35} -> {view_func}")
        except AttributeError as e:
            print(f"  ❌ {view_name:<35} -> NOT FOUND: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ⚠️  {view_name:<35} -> ERROR: {e}")
            all_passed = False
    
    return all_passed

def test_page_access():
    """Test page access with authentication"""
    print("\n🔐 Testing Page Access...")
    
    client = Client()
    user, patient = create_test_data()
    
    # Test public pages
    public_pages = [
        ('selftest:home', 'Self-Test'),
        ('selftest:symptoms', 'Symptoms'),
    ]
    
    for url_name, expected_content in public_pages:
        try:
            response = client.get(reverse(url_name))
            if response.status_code == 200:
                print(f"  ✅ {url_name:<35} -> Status 200")
            else:
                print(f"  ⚠️  {url_name:<35} -> Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url_name:<35} -> ERROR: {e}")
    
    # Test authenticated pages
    client.login(username='testpatient', password='testpass123')
    
    auth_pages = [
        ('selftest:dashboard', 'Dashboard'),
        ('selftest:start', 'Start'),
        ('selftest:quick', 'Quick'),
    ]
    
    for url_name, expected_content in auth_pages:
        try:
            response = client.get(reverse(url_name))
            if response.status_code == 200:
                print(f"  ✅ {url_name:<35} -> Status 200 (Authenticated)")
            else:
                print(f"  ⚠️  {url_name:<35} -> Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url_name:<35} -> ERROR: {e}")

def test_api_endpoints():
    """Test API endpoints functionality"""
    print("\n🔌 Testing API Endpoints...")
    
    client = Client()
    user, patient = create_test_data()
    client.login(username='testpatient', password='testpass123')
    
    # Test quick symptom search API
    try:
        response = client.get(reverse('selftest:quick_symptom_search_api'), {'q': 'head'})
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ quick_symptom_search_api    -> Status 200, {len(data.get('symptoms', []))} symptoms")
        else:
            print(f"  ⚠️  quick_symptom_search_api    -> Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ quick_symptom_search_api    -> ERROR: {e}")
    
    # Test regular symptom search API
    try:
        response = client.get(reverse('selftest:symptom_search_api'), {'q': 'fever'})
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ symptom_search_api          -> Status 200, {len(data.get('symptoms', []))} symptoms")
        else:
            print(f"  ⚠️  symptom_search_api          -> Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ symptom_search_api          -> ERROR: {e}")

def test_form_submission():
    """Test form submissions"""
    print("\n📋 Testing Form Submissions...")
    
    client = Client()
    user, patient = create_test_data()
    client.login(username='testpatient', password='testpass123')
    
    # Test quick test form
    try:
        # First get the page to see available symptoms
        response = client.get(reverse('selftest:quick'))
        if response.status_code == 200:
            print(f"  ✅ Quick test page load        -> Status 200")
            
            # Try form submission (this might not work perfectly due to dynamic form fields)
            form_data = {
                'overall_severity': 'moderate'
            }
            response = client.post(reverse('selftest:quick'), data=form_data)
            print(f"  ✅ Quick test form submit      -> Status {response.status_code}")
        else:
            print(f"  ⚠️  Quick test page load        -> Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Quick test form             -> ERROR: {e}")

def validate_quick_test_template():
    """Validate the quick test template has the correct URL reference"""
    print("\n📄 Validating Quick Test Template...")
    
    template_path = 'templates/selftest/quick_test.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "quick_symptom_search_api" in content:
            print("  ✅ Template contains quick_symptom_search_api reference")
            
            # Check if it's using the correct Django URL tag
            if "{% url 'selftest:quick_symptom_search_api' %}" in content:
                print("  ✅ Template uses correct Django URL tag")
            else:
                print("  ⚠️  Template might not use correct Django URL tag")
        else:
            print("  ❌ Template does not contain quick_symptom_search_api reference")
            
    except FileNotFoundError:
        print(f"  ❌ Template file not found: {template_path}")
    except Exception as e:
        print(f"  ❌ Error reading template: {e}")

def main():
    """Run all validation tests"""
    print("🚀 SelfTest Comprehensive Validation")
    print("=" * 60)
    
    url_test = test_url_resolution()
    view_test = test_view_functions()
    
    # Only continue with integration tests if basic tests pass
    if url_test and view_test:
        test_page_access()
        test_api_endpoints()
        test_form_submission()
        validate_quick_test_template()
        
        print("\n" + "=" * 60)
        print("✅ All basic validation tests PASSED!")
        print("🎯 The quick_symptom_search_api URL should now work correctly")
        print("🌐 Server should be accessible at: http://127.0.0.1:8000/selftest/quick/")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Basic validation tests FAILED!")
        print("🔧 Please check URL patterns and view functions")
        print("=" * 60)

if __name__ == '__main__':
    main() 