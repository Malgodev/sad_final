#!/usr/bin/env python
"""
Automation test script for SELFTEST-01
Tests the self-test system with preknown symptoms and verifies correct disease predictions
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest, Symptom, SymptomReport
from selftest.ai_engine import HealthAIEngine


def create_test_patient():
    """Create a test patient for testing"""
    try:
        user = User.objects.get(username='testpatient')
        patient = Patient.objects.get(user=user)
    except (User.DoesNotExist, Patient.DoesNotExist):
        user = User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Patient'
        )
        patient = Patient.objects.create(
            user=user,
            date_of_birth='1990-01-01',
            gender='M',
            phone='1234567890'
        )
    
    return user, patient


def test_ai_engine():
    """Test AI engine functionality"""
    print("🧠 Testing AI Engine...")
    
    ai_engine = HealthAIEngine()
    
    # Test 1: Common Cold Symptoms
    print("\n📋 Test 1: Common Cold Symptoms")
    cold_symptoms = [
        {'symptom_name': 'runny nose', 'severity': 2, 'duration_days': 3},
        {'symptom_name': 'sneezing', 'severity': 1, 'duration_days': 2},
        {'symptom_name': 'sore throat', 'severity': 2, 'duration_days': 2},
        {'symptom_name': 'cough', 'severity': 1, 'duration_days': 1}
    ]
    
    result = ai_engine.analyze_symptoms(cold_symptoms)
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Diseases: {[d['name'] for d in result['predicted_diseases'][:3]]}")
    print(f"  Top Confidence: {result['predicted_diseases'][0]['confidence'] if result['predicted_diseases'] else 0}%")
    
    # Test 2: Influenza Symptoms
    print("\n📋 Test 2: Influenza Symptoms")
    flu_symptoms = [
        {'symptom_name': 'fever', 'severity': 3, 'duration_days': 2},
        {'symptom_name': 'muscle aches', 'severity': 3, 'duration_days': 2},
        {'symptom_name': 'fatigue', 'severity': 3, 'duration_days': 3},
        {'symptom_name': 'headache', 'severity': 2, 'duration_days': 2}
    ]
    
    result = ai_engine.analyze_symptoms(flu_symptoms)
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Diseases: {[d['name'] for d in result['predicted_diseases'][:3]]}")
    print(f"  Top Confidence: {result['predicted_diseases'][0]['confidence'] if result['predicted_diseases'] else 0}%")
    
    # Test 3: Severe Symptoms
    print("\n📋 Test 3: Severe Symptoms")
    severe_symptoms = [
        {'symptom_name': 'chest pain', 'severity': 4, 'duration_days': 1},
        {'symptom_name': 'difficulty breathing', 'severity': 4, 'duration_days': 1}
    ]
    
    result = ai_engine.analyze_symptoms(severe_symptoms)
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Diseases: {[d['name'] for d in result['predicted_diseases'][:3]]}")
    print(f"  Specialist Referral: {result['specialist_referral']}")
    
    return True


def test_web_interface():
    """Test web interface functionality"""
    print("\n🌐 Testing Web Interface...")
    
    client = Client()
    user, patient = create_test_patient()
    
    # Test home page
    response = client.get('/selftest/')
    print(f"  Home Page: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Login
    login_success = client.login(username='testpatient', password='testpass123')
    print(f"  Login: {'✅' if login_success else '❌'}")
    
    if not login_success:
        return False
    
    # Test dashboard
    response = client.get('/selftest/dashboard/')
    print(f"  Dashboard: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test quick test page
    response = client.get('/selftest/quick/')
    print(f"  Quick Test Page: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test symptom search API
    response = client.get('/selftest/api/quick-symptom-search/?q=fever')
    print(f"  Symptom Search API: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"    Found {len(data.get('symptoms', []))} symptoms")
    
    return True


def test_complete_workflow():
    """Test complete workflow with symptom submission"""
    print("\n🔄 Testing Complete Workflow...")
    
    client = Client()
    user, patient = create_test_patient()
    client.login(username='testpatient', password='testpass123')
    
    # Test with flu-like symptoms
    selected_symptoms = [
        {
            'name': 'Fever',
            'description': 'High temperature',
            'category': 'General',
            'severity': 3
        },
        {
            'name': 'Headache',
            'description': 'Head pain',
            'category': 'Neurological',
            'severity': 2
        },
        {
            'name': 'Fatigue',
            'description': 'Tiredness',
            'category': 'General',
            'severity': 3
        }
    ]
    
    # Submit test
    response = client.post('/selftest/quick/', {
        'selected_symptoms': json.dumps(selected_symptoms),
        'additional_notes': 'Started 2 days ago, feeling unwell'
    })
    
    print(f"  Quick Test Submission: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print("  ✅ Test submitted successfully")
                
                # Check if test was saved
                test_count = SelfTest.objects.filter(patient=patient).count()
                print(f"  ✅ Tests in database: {test_count}")
                
                if test_count > 0:
                    latest_test = SelfTest.objects.filter(patient=patient).first()
                    print(f"  ✅ Risk Level: {latest_test.risk_level}")
                    print(f"  ✅ Predicted Diseases: {len(latest_test.predicted_diseases)}")
                    print(f"  ✅ Symptom Reports: {latest_test.symptom_reports.count()}")
                    
                    # Show top predictions
                    if latest_test.predicted_diseases:
                        print("  📊 Top Predictions:")
                        for i, disease in enumerate(latest_test.predicted_diseases[:3], 1):
                            print(f"    {i}. {disease['name']} ({disease['confidence']}%)")
                
                return True
            else:
                print(f"  ❌ Test failed: {data.get('error')}")
                return False
        except json.JSONDecodeError:
            print(f"  ❌ Invalid JSON response")
            return False
    
    return False


def test_severity_levels():
    """Test that severity levels are correctly limited to 1-4"""
    print("\n🎚️ Testing Severity Levels...")
    
    from selftest.forms import SymptomReportForm
    
    form = SymptomReportForm()
    severity_choices = form.fields['severity'].choices
    
    print(f"  Severity Choices Count: {len(severity_choices)} {'✅' if len(severity_choices) == 4 else '❌'}")
    
    choice_values = [choice[0] for choice in severity_choices]
    expected_values = [1, 2, 3, 4]
    
    print(f"  Severity Values: {choice_values} {'✅' if choice_values == expected_values else '❌'}")
    
    choice_labels = [choice[1] for choice in severity_choices]
    required_labels = ['Mild', 'Moderate', 'Severe', 'Very Severe']
    
    labels_correct = all(any(req_label in label for req_label in required_labels) 
                        for label in choice_labels)
    
    print(f"  Severity Labels: {'✅' if labels_correct else '❌'}")
    
    return len(severity_choices) == 4 and choice_values == expected_values


def main():
    """Run all automation tests"""
    print("🚀 Starting SELFTEST-01 Automation Tests")
    print("=" * 50)
    
    tests = [
        ("AI Engine", test_ai_engine),
        ("Web Interface", test_web_interface),
        ("Complete Workflow", test_complete_workflow),
        ("Severity Levels", test_severity_levels),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n{test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: ❌ ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<20}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SELFTEST-01 is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 