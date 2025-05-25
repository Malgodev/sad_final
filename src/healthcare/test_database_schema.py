#!/usr/bin/env python
"""
Test script to verify database schema
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest, Symptom, SymptomReport

def test_database_schema():
    """Test the database schema"""
    print("🔍 Testing Database Schema...")
    
    # Check if tables exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Available tables: {tables}")
        
        # Check selftest_selftest table structure
        if 'selftest_selftest' in tables:
            cursor.execute("PRAGMA table_info(selftest_selftest);")
            columns = cursor.fetchall()
            print(f"📊 selftest_selftest columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ selftest_selftest table not found")
            return False
    
    return True

def test_model_creation():
    """Test creating models"""
    print("\n🧪 Testing Model Creation...")
    
    try:
        # Create test user and patient
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
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
            name='Test Fever',
            defaults={
                'description': 'Test fever symptom',
                'category': 'General'
            }
        )
        
        print(f"✅ Symptom created: {symptom}")
        
        # Create test self-test
        selftest = SelfTest.objects.create(
            patient=patient,
            risk_level='low',
            ai_recommendation='Test recommendation',
            predicted_diseases=[{'name': 'Test Disease', 'confidence': 50}],
            additional_notes='Test notes'
        )
        
        print(f"✅ SelfTest created: {selftest}")
        
        # Create symptom report
        symptom_report = SymptomReport.objects.create(
            self_test=selftest,
            symptom=symptom,
            severity=2,
            duration_days=3,
            notes='Test symptom report'
        )
        
        print(f"✅ SymptomReport created: {symptom_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating models: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Database Schema Test")
    print("=" * 40)
    
    schema_ok = test_database_schema()
    model_ok = test_model_creation()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"  Database Schema: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"  Model Creation: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if schema_ok and model_ok:
        print("🎉 All tests passed! Database is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 