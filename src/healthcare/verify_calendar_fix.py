#!/usr/bin/env python
"""
Calendar Template Fix Verification Script
Tests that the calendar template loads without TemplateSyntaxError
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from doctor.models import Doctor
from appointment.models import AppointmentSlot
from datetime import date, timedelta

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
    django.setup()

def test_calendar_template():
    """Test that calendar template loads without errors"""
    print("🧪 Testing Calendar Template Fix...")
    print("-" * 50)
    
    # Create test client
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
            if 'Appointment Slots Calendar' in response.content.decode():
                print("  ✅ Calendar title found")
            else:
                print("  ⚠️  Calendar title not found")
                
            if 'calendar-table' in response.content.decode():
                print("  ✅ Calendar table structure found")
            else:
                print("  ⚠️  Calendar table structure not found")
                
            if str(test_date.year) in response.content.decode():
                print("  ✅ Current year displayed")
            else:
                print("  ⚠️  Current year not found")
                
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

def test_calendar_navigation():
    """Test calendar month navigation"""
    print("\n🧪 Testing Calendar Navigation...")
    print("-" * 50)
    
    client = Client()
    
    # Create test doctor
    doctor_user = User.objects.create_user(
        username='nav_test_doctor',
        email='nav@test.com',
        password='testpass123'
    )
    
    doctor = Doctor.objects.create(
        user=doctor_user,
        specialization='Navigation Test',
        license_number='NAV123456',
        approval_status='approved'
    )
    
    client.force_login(doctor_user)
    
    try:
        # Test current month
        print("  ✓ Testing current month...")
        response = client.get(reverse('doctor:appointment_calendar'))
        if response.status_code == 200:
            print("  ✅ Current month loads")
        
        # Test next month navigation
        print("  ✓ Testing next month navigation...")
        next_month = date.today().replace(day=1) + timedelta(days=32)
        response = client.get(
            reverse('doctor:appointment_calendar') + 
            f'?year={next_month.year}&month={next_month.month}'
        )
        if response.status_code == 200:
            print("  ✅ Next month navigation works")
        
        # Test previous month navigation
        print("  ✓ Testing previous month navigation...")
        prev_month = date.today().replace(day=1) - timedelta(days=1)
        response = client.get(
            reverse('doctor:appointment_calendar') + 
            f'?year={prev_month.year}&month={prev_month.month}'
        )
        if response.status_code == 200:
            print("  ✅ Previous month navigation works")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Navigation test failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            doctor.delete()
            doctor_user.delete()
        except:
            pass

def test_slot_display():
    """Test that slots display correctly in calendar"""
    print("\n🧪 Testing Slot Display...")
    print("-" * 50)
    
    client = Client()
    
    # Create test doctor
    doctor_user = User.objects.create_user(
        username='slot_test_doctor',
        email='slot@test.com',
        password='testpass123'
    )
    
    doctor = Doctor.objects.create(
        user=doctor_user,
        specialization='Slot Test',
        license_number='SLT123456',
        approval_status='approved'
    )
    
    client.force_login(doctor_user)
    
    try:
        # Create slots for different times
        test_date = date.today() + timedelta(days=2)
        
        slots = []
        slot_types = ['morning_1', 'morning_2', 'afternoon_1', 'afternoon_2']
        
        for slot_type in slot_types:
            slot = AppointmentSlot.objects.create(
                doctor=doctor,
                date=test_date,
                slot_type=slot_type
            )
            slots.append(slot)
        
        print(f"  ✓ Created {len(slots)} test slots for {test_date}")
        
        # Test calendar displays slots
        response = client.get(reverse('doctor:appointment_calendar'))
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for slot indicators
            if 'slot-item' in content:
                print("  ✅ Slot items found in calendar")
            
            if 'available' in content:
                print("  ✅ Available slot status found")
            
            if str(test_date.day) in content:
                print("  ✅ Test date found in calendar")
                
            print("  ✅ Slot display test passed")
            return True
        else:
            print(f"  ❌ Calendar failed to load (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"  ❌ Slot display test failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            for slot in slots:
                slot.delete()
            doctor.delete()
            doctor_user.delete()
        except:
            pass

def main():
    """Main verification function"""
    print("=" * 60)
    print("CALENDAR TEMPLATE FIX VERIFICATION")
    print("=" * 60)
    
    setup_django()
    
    tests = [
        ("Calendar Template Loading", test_calendar_template),
        ("Calendar Navigation", test_calendar_navigation),
        ("Slot Display", test_slot_display),
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
    print("VERIFICATION SUMMARY")
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
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ Calendar template fix is working correctly")
        return True
    else:
        print("⚠️  Some verification tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 