#!/usr/bin/env python
"""
Test script to verify selftest functionality after database fix
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest, Symptom, SymptomReport

def test_database_creation():
    """Test creating records in the database"""
    print("🧪 Testing Database Record Creation...")
    
    try:
        # Create test user and patient
        user, created = User.objects.get_or_create(
            username='testpatient_fix',
            defaults={
                'email': 'testfix@example.com',
                'first_name': 'Test',
                'last_name': 'Patient'
            }
        )
        
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'date_of_birth': '1990-01-01',
                'gender': 'M',
                'phone': '1234567890'
            }
        )
        
        print(f"✅ Patient created: {patient}")
        
        # Create test symptom
        symptom, created = Symptom.objects.get_or_create(
            name='Test Headache',
            defaults={
                'description': 'Test headache symptom',
                'category': 'Neurological'
            }
        )
        
        print(f"✅ Symptom created: {symptom}")
        
        # Create test self-test with patient field
        selftest = SelfTest.objects.create(
            patient=patient,  # This should work now
            risk_level='medium',
            ai_recommendation='Test recommendation for headache',
            predicted_diseases=[{'name': 'Tension Headache', 'confidence': 75}],
            additional_notes='Test notes'
        )
        
        print(f"✅ SelfTest created with patient field: {selftest}")
        print(f"   - ID: {selftest.id}")
        print(f"   - Patient: {selftest.patient}")
        print(f"   - Risk Level: {selftest.risk_level}")
        
        # Create symptom report
        symptom_report = SymptomReport.objects.create(
            self_test=selftest,
            symptom=symptom,
            severity=3,  # Severe (1-4 scale)
            duration_days=2,
            notes='Persistent headache for 2 days'
        )
        
        print(f"✅ SymptomReport created: {symptom_report}")
        print(f"   - Severity: {symptom_report.severity}/4")
        print(f"   - Duration: {symptom_report.duration_days} days")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating records: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface():
    """Test the web interface"""
    print("\n🌐 Testing Web Interface...")
    
    try:
        # Test if the selftest page loads
        response = requests.get('http://127.0.0.1:8000/selftest/', timeout=5)
        if response.status_code == 200:
            print("✅ Selftest page loads successfully")
            return True
        else:
            print(f"❌ Selftest page returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing web interface: {str(e)}")
        print("   Make sure the Django server is running on 127.0.0.1:8000")
        return False

def main():
    """Run all tests"""
    print("🚀 SelfTest Database Fix Verification")
    print("=" * 50)
    
    db_ok = test_database_creation()
    web_ok = test_web_interface()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Database Creation: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"  Web Interface: {'✅ PASS' if web_ok else '❌ FAIL'}")
    
    if db_ok and web_ok:
        print("🎉 All tests passed! The patient_id issue is fixed.")
        print("💡 You can now use the selftest feature without errors.")
        return True
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 