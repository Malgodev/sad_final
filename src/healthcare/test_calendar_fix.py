#!/usr/bin/env python
"""
Simple Test Script to Verify Calendar Fix and Core Doctor Appointment Functionality
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

# Now import Django modules
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from doctor.models import Doctor
from appointment.models import AppointmentSlot

def test_calendar_template_fix():
    """Test that the calendar template loads without TemplateSyntaxError"""
    print("🧪 Testing Calendar Template Fix...")
    print("-" * 50)
    
    client = Client()
    
    # Create test doctor
    doctor_user = User.objects.create_user(
        username='test_calendar_doctor',
        email='calendar@test.com',
        password='testpass123',
        first_name='Calendar',
        last_name='Test'
    )
    
    doctor = Doctor.objects.create(
        user=doctor_user,
        specialization='Test Specialty',
        license_number='CAL123456',
        phone='555-0000',
        experience_years=1,
        approval_status='approved'
    )
    
    # Create test appointment slot
    test_date = date.today() + timedelta(days=1)
    slot = AppointmentSlot.objects.create(
        doctor=doctor,
        date=test_date,
        slot_type='morning_1'
    )
    
    # Login as doctor
    client.force_login(doctor_user)
    
    try:
        # Test calendar view
        print("  ✓ Testing calendar view...")
        response = client.get(reverse('doctor:appointment_calendar'))
        
        if response.status_code == 200:
            print("  ✅ Calendar loads successfully (Status: 200)")
            
            # Check for key content
            content = response.content.decode()
            if 'Appointment Slots Calendar' in content:
                print("  ✅ Calendar title found")
            
            if 'calendar-table' in content:
                print("  ✅ Calendar table structure found")
            
            if str(test_date.year) in content:
                print("  ✅ Current year displayed")
                
            if 'slot-item' in content:
                print("  ✅ Slot items rendered")
                
            print(f"  ✅ Template rendered successfully ({len(response.content)} bytes)")
            return True
            
        else:
            print(f"  ❌ Calendar failed to load (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"  ❌ Error loading calendar: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            slot.delete()
            doctor.delete()
            doctor_user.delete()
            print("  🧹 Test data cleaned up")
        except:
            pass

def test_core_functionality():
    """Test core doctor appointment functionality"""
    print("\n🧪 Testing Core Doctor Appointment Functionality...")
    print("-" * 50)
    
    client = Client()
    
    # Create test doctor
    doctor_user = User.objects.create_user(
        username='test_core_doctor',
        email='core@test.com',
        password='testpass123',
        first_name='Core',
        last_name='Test'
    )
    
    doctor = Doctor.objects.create(
        user=doctor_user,
        specialization='Core Test',
        license_number='CORE123456',
        phone='555-1111',
        experience_years=2,
        approval_status='approved'
    )
    
    client.force_login(doctor_user)
    
    try:
        # Test 1: Dashboard access
        print("  ✓ Testing dashboard access...")
        response = client.get(reverse('doctor:dashboard'))
        if response.status_code == 200:
            print("  ✅ Dashboard loads successfully")
        else:
            print(f"  ❌ Dashboard failed (Status: {response.status_code})")
            return False
        
        # Test 2: Create appointment slots view
        print("  ✓ Testing create slots view...")
        response = client.get(reverse('doctor:create_appointment_slots'))
        if response.status_code == 200:
            print("  ✅ Create slots view loads")
        else:
            print(f"  ❌ Create slots view failed (Status: {response.status_code})")
            return False
        
        # Test 3: Bulk create slots view
        print("  ✓ Testing bulk create view...")
        response = client.get(reverse('doctor:bulk_create_slots'))
        if response.status_code == 200:
            print("  ✅ Bulk create view loads")
        else:
            print(f"  ❌ Bulk create view failed (Status: {response.status_code})")
            return False
        
        # Test 4: Appointment list view
        print("  ✓ Testing appointment list view...")
        response = client.get(reverse('doctor:appointment_list'))
        if response.status_code == 200:
            print("  ✅ Appointment list view loads")
        else:
            print(f"  ❌ Appointment list view failed (Status: {response.status_code})")
            return False
        
        # Test 5: Create a slot and test slot detail
        print("  ✓ Testing slot creation and detail view...")
        test_date = date.today() + timedelta(days=2)
        slot = AppointmentSlot.objects.create(
            doctor=doctor,
            date=test_date,
            slot_type='afternoon_1'
        )
        
        response = client.get(reverse('doctor:slot_detail', args=[slot.id]))
        if response.status_code == 200:
            print("  ✅ Slot detail view loads")
        else:
            print(f"  ❌ Slot detail view failed (Status: {response.status_code})")
            return False
        
        print("  ✅ All core functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in core functionality test: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            doctor.delete()
            doctor_user.delete()
            print("  🧹 Test data cleaned up")
        except:
            pass

def main():
    """Main test function"""
    print("=" * 60)
    print("DOCTOR APPOINTMENT SYSTEM - CALENDAR FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Calendar Template Fix", test_calendar_template_fix),
        ("Core Functionality", test_core_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Calendar template fix is working correctly")
        print("✅ Core doctor appointment functionality is working")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 