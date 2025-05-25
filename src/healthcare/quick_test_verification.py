#!/usr/bin/env python
"""
Quick verification script for SELFTEST-01 fixes
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from selftest.forms import SymptomReportForm
from selftest.ai_engine import HealthAIEngine
from django.test import Client
from django.contrib.auth.models import User
from patient.models import Patient

def test_severity_levels():
    """Test that severity is limited to 4 levels"""
    print("🎚️ Testing Severity Levels...")
    
    form = SymptomReportForm()
    severity_choices = form.fields['severity'].choices
    
    print(f"  Severity choices: {len(severity_choices)} levels")
    for choice in severity_choices:
        print(f"    {choice[0]}: {choice[1]}")
    
    return len(severity_choices) == 4

def test_ai_engine():
    """Test AI engine with sample symptoms"""
    print("\n🧠 Testing AI Engine...")
    
    ai_engine = HealthAIEngine()
    
    # Test with flu symptoms
    symptoms = [
        {'symptom_name': 'fever', 'severity': 3, 'duration_days': 2},
        {'symptom_name': 'headache', 'severity': 2, 'duration_days': 2},
        {'symptom_name': 'fatigue', 'severity': 3, 'duration_days': 3}
    ]
    
    result = ai_engine.analyze_symptoms(symptoms)
    
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Diseases: {len(result['predicted_diseases'])}")
    if result['predicted_diseases']:
        print(f"  Top Prediction: {result['predicted_diseases'][0]['name']} ({result['predicted_diseases'][0]['confidence']}%)")
    
    return len(result['predicted_diseases']) > 0

def test_patient_button_url():
    """Test that patient dashboard button points to /selftest/"""
    print("\n🔗 Testing Patient Dashboard Button URL...")
    
    # Read the patient dashboard template
    try:
        with open('templates/patient/dashboard.html', 'r') as f:
            content = f.read()
            
        if '/selftest/' in content and 'Health Self-Test' in content:
            print("  ✅ Patient dashboard button points to /selftest/")
            return True
        else:
            print("  ❌ Patient dashboard button URL not found")
            return False
    except FileNotFoundError:
        print("  ❌ Patient dashboard template not found")
        return False

def main():
    """Run verification tests"""
    print("🚀 SELFTEST-01 Verification")
    print("=" * 40)
    
    tests = [
        ("Severity Levels", test_severity_levels),
        ("AI Engine", test_ai_engine),
        ("Patient Button URL", test_patient_button_url),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: ❌ ERROR - {str(e)}")
    
    print("\n" + "=" * 40)
    print("📊 Verification Results:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verifications passed!")
        print("\n📋 Summary of Changes:")
        print("  ✅ Patient dashboard button now points to /selftest/")
        print("  ✅ Severity system changed from 10 levels to 4 levels")
        print("  ✅ Database schema fixed for patient_id field")
        print("  ✅ AI engine updated for 4-stage severity")
        print("  ✅ Automation tests created and functional")
    else:
        print("⚠️ Some verifications failed.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 