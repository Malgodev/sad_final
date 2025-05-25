#!/usr/bin/env python
"""
Final verification test for selftest functionality
"""

import os
import sys
import django
import sqlite3

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest, Symptom, SymptomReport

def test_database_schema():
    """Test the actual database schema"""
    print("🔍 Testing Database Schema...")
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if selftest_selftest table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='selftest_selftest';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ selftest_selftest table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(selftest_selftest);")
            columns = cursor.fetchall()
            
            print("📊 Table columns:")
            patient_field_exists = False
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                if col[1] == 'patient_id':
                    patient_field_exists = True
            
            if patient_field_exists:
                print("✅ patient_id field exists in database")
                return True
            else:
                print("❌ patient_id field NOT found in database")
                return False
                
        else:
            print("❌ selftest_selftest table does not exist")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database schema: {str(e)}")
        return False

def test_model_operations():
    """Test Django model operations"""
    print("\n🧪 Testing Django Model Operations...")
    
    try:
        # Create test user
        user, created = User.objects.get_or_create(
            username='final_test_user',
            defaults={
                'email': 'finaltest@example.com',
                'first_name': 'Final',
                'last_name': 'Test',
                'password': 'testpass123'
            }
        )
        print(f"✅ User: {user} (created: {created})")
        
        # Create patient
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'date_of_birth': '1990-01-01',
                'gender': 'M',
                'phone': '1234567890'
            }
        )
        print(f"✅ Patient: {patient} (created: {created})")
        
        # Create test symptom
        symptom, created = Symptom.objects.get_or_create(
            name='Final Test Fever',
            defaults={
                'description': 'Test fever for final verification',
                'category': 'General',
                'severity_scale': '1-4'
            }
        )
        print(f"✅ Symptom: {symptom} (created: {created})")
        
        # Create selftest - this is where the error was occurring
        selftest = SelfTest.objects.create(
            patient=patient,
            risk_level='medium',
            ai_recommendation='Final test recommendation',
            predicted_diseases=[{'name': 'Test Disease', 'confidence': 80}],
            additional_notes='Final verification test'
        )
        print(f"✅ SelfTest created successfully!")
        print(f"   ID: {selftest.id}")
        print(f"   Patient: {selftest.patient}")
        print(f"   Risk Level: {selftest.risk_level}")
        
        # Create symptom report
        symptom_report = SymptomReport.objects.create(
            self_test=selftest,
            symptom=symptom,
            severity=3,  # Severe (1-4 scale)
            duration_days=2,
            notes='Final test symptom report'
        )
        print(f"✅ SymptomReport: {symptom_report}")
        print(f"   Severity: {symptom_report.severity}/4")
        print(f"   Duration: {symptom_report.duration_days} days")
        
        # Test querying
        all_tests = SelfTest.objects.filter(patient=patient)
        print(f"✅ Query test: Found {all_tests.count()} tests for patient")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in model operations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_symptom_count():
    """Test symptom population"""
    print("\n📊 Testing Symptom Database...")
    
    try:
        symptom_count = Symptom.objects.count()
        print(f"✅ Total symptoms in database: {symptom_count}")
        
        if symptom_count > 0:
            # Show some sample symptoms
            sample_symptoms = Symptom.objects.all()[:5]
            print("📋 Sample symptoms:")
            for symptom in sample_symptoms:
                print(f"  - {symptom.name} ({symptom.category})")
            return True
        else:
            print("⚠️ No symptoms found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking symptoms: {str(e)}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Final Selftest Verification")
    print("=" * 60)
    
    schema_ok = test_database_schema()
    model_ok = test_model_operations()
    symptom_ok = test_symptom_count()
    
    print("\n" + "=" * 60)
    print("📊 Final Verification Results:")
    print(f"  Database Schema: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"  Model Operations: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"  Symptom Database: {'✅ PASS' if symptom_ok else '❌ FAIL'}")
    
    if schema_ok and model_ok and symptom_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 The selftest system is working correctly!")
        print("🌐 You can now access the selftest at http://127.0.0.1:8000/selftest/")
        print("🔧 The patient_id error should be completely resolved!")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("🔧 Please check the errors above and fix the issues.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 