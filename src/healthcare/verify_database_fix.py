#!/usr/bin/env python
"""
Comprehensive database verification script
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

def check_database_schema():
    """Check the actual database schema"""
    print("🔍 Checking Database Schema...")
    
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
            else:
                print("❌ patient_id field NOT found in database")
                
        else:
            print("❌ selftest_selftest table does not exist")
            
        conn.close()
        return table_exists and patient_field_exists
        
    except Exception as e:
        print(f"❌ Error checking database schema: {str(e)}")
        return False

def test_model_operations():
    """Test Django model operations"""
    print("\n🧪 Testing Django Model Operations...")
    
    try:
        # Create test user
        user, created = User.objects.get_or_create(
            username='verify_test',
            defaults={
                'email': 'verify@example.com',
                'first_name': 'Verify',
                'last_name': 'Test'
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
        
        # Create selftest - this is where the error occurs
        selftest = SelfTest.objects.create(
            patient=patient,
            risk_level='medium',
            ai_recommendation='Verification test recommendation',
            predicted_diseases=[{'name': 'Test Disease', 'confidence': 80}],
            additional_notes='Database verification test'
        )
        print(f"✅ SelfTest created successfully!")
        print(f"   ID: {selftest.id}")
        print(f"   Patient: {selftest.patient}")
        print(f"   Risk Level: {selftest.risk_level}")
        
        # Test symptom creation
        symptom, created = Symptom.objects.get_or_create(
            name='Verification Headache',
            defaults={
                'description': 'Test headache for verification',
                'category': 'Neurological'
            }
        )
        print(f"✅ Symptom: {symptom} (created: {created})")
        
        # Test symptom report
        symptom_report = SymptomReport.objects.create(
            self_test=selftest,
            symptom=symptom,
            severity=3,
            duration_days=2,
            notes='Verification test symptom report'
        )
        print(f"✅ SymptomReport: {symptom_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in model operations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_migration_status():
    """Check Django migration status"""
    print("\n📋 Checking Migration Status...")
    
    try:
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("❌ Pending migrations found:")
            for migration, backwards in plan:
                print(f"  - {migration}")
            return False
        else:
            print("✅ All migrations are up to date")
            return True
            
    except Exception as e:
        print(f"❌ Error checking migrations: {str(e)}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Database Verification Script")
    print("=" * 50)
    
    schema_ok = check_database_schema()
    migration_ok = check_migration_status()
    model_ok = test_model_operations()
    
    print("\n" + "=" * 50)
    print("📊 Verification Results:")
    print(f"  Database Schema: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"  Migration Status: {'✅ PASS' if migration_ok else '❌ FAIL'}")
    print(f"  Model Operations: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if schema_ok and migration_ok and model_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 The database is correctly configured and ready to use.")
        print("🌐 You can now access the selftest at http://127.0.0.1:8000/selftest/")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("🔧 Please check the errors above and fix the issues.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 