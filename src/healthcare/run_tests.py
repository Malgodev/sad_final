#!/usr/bin/env python
"""
Automated Test Runner for Doctor Appointment System
Runs comprehensive tests to validate all doctor appointment functionality
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
    django.setup()

def run_doctor_appointment_tests():
    """Run all doctor appointment tests"""
    print("=" * 80)
    print("DOCTOR APPOINTMENT SYSTEM - AUTOMATED TEST SUITE")
    print("=" * 80)
    print()
    
    # Setup Django
    setup_django()
    
    # Test categories to run
    test_modules = [
        'doctor.tests.DoctorAppointmentTestCase',
        'doctor.tests.DoctorAppointmentIntegrationTest',
    ]
    
    print("Running the following test modules:")
    for module in test_modules:
        print(f"  ✓ {module}")
    print()
    
    # Run tests with verbose output
    test_command = [
        'manage.py',
        'test',
        '--verbosity=2',
        '--keepdb',  # Keep test database for faster subsequent runs
        'doctor.tests'
    ]
    
    try:
        execute_from_command_line(test_command)
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        return True
    except SystemExit as e:
        if e.code == 0:
            print("\n" + "=" * 80)
            print("✅ ALL TESTS PASSED!")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("❌ SOME TESTS FAILED!")
            print("=" * 80)
            return False
    except Exception as e:
        print(f"\n❌ ERROR RUNNING TESTS: {e}")
        return False

def run_specific_test_categories():
    """Run specific categories of tests"""
    print("\nRunning specific test categories:")
    print("-" * 50)
    
    categories = {
        "Authentication Tests": [
            'doctor.tests.DoctorAppointmentTestCase.test_doctor_authentication_required',
            'doctor.tests.DoctorAppointmentTestCase.test_doctor_login_and_dashboard_access',
            'doctor.tests.DoctorAppointmentTestCase.test_doctor_approval_required',
        ],
        "Calendar & Views Tests": [
            'doctor.tests.DoctorAppointmentTestCase.test_appointment_calendar_view',
            'doctor.tests.DoctorAppointmentTestCase.test_calendar_navigation',
        ],
        "Slot Management Tests": [
            'doctor.tests.DoctorAppointmentTestCase.test_create_appointment_slots_view',
            'doctor.tests.DoctorAppointmentTestCase.test_bulk_create_slots_view',
            'doctor.tests.DoctorAppointmentTestCase.test_slot_detail_view',
            'doctor.tests.DoctorAppointmentTestCase.test_delete_empty_slot',
            'doctor.tests.DoctorAppointmentTestCase.test_cannot_delete_booked_slot',
        ],
        "Appointment Management Tests": [
            'doctor.tests.DoctorAppointmentTestCase.test_slot_detail_with_patient',
            'doctor.tests.DoctorAppointmentTestCase.test_update_appointment_status',
            'doctor.tests.DoctorAppointmentTestCase.test_appointment_list_view',
        ],
        "Integration Tests": [
            'doctor.tests.DoctorAppointmentIntegrationTest.test_complete_appointment_workflow',
            'doctor.tests.DoctorAppointmentIntegrationTest.test_bulk_slot_creation_and_management',
        ]
    }
    
    for category, tests in categories.items():
        print(f"\n🧪 {category}:")
        for test in tests:
            print(f"   • {test.split('.')[-1]}")
    
    return categories

def run_quick_smoke_tests():
    """Run quick smoke tests to verify basic functionality"""
    print("\n🚀 Running Quick Smoke Tests...")
    print("-" * 40)
    
    smoke_tests = [
        'doctor.tests.DoctorAppointmentTestCase.test_doctor_authentication_required',
        'doctor.tests.DoctorAppointmentTestCase.test_appointment_calendar_view',
        'doctor.tests.DoctorAppointmentTestCase.test_create_appointment_slots_view',
        'doctor.tests.DoctorAppointmentTestCase.test_slot_detail_view',
    ]
    
    test_command = [
        'manage.py',
        'test',
        '--verbosity=1',
        '--keepdb',
    ] + smoke_tests
    
    try:
        execute_from_command_line(test_command)
        print("✅ Smoke tests passed!")
        return True
    except SystemExit as e:
        if e.code == 0:
            print("✅ Smoke tests passed!")
            return True
        else:
            print("❌ Smoke tests failed!")
            return False

def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--smoke':
            setup_django()
            return run_quick_smoke_tests()
        elif sys.argv[1] == '--categories':
            setup_django()
            categories = run_specific_test_categories()
            print(f"\nFound {sum(len(tests) for tests in categories.values())} total tests across {len(categories)} categories")
            return True
        elif sys.argv[1] == '--help':
            print("Doctor Appointment Test Runner")
            print("Usage:")
            print("  python run_tests.py           # Run all tests")
            print("  python run_tests.py --smoke   # Run quick smoke tests")
            print("  python run_tests.py --categories # Show test categories")
            print("  python run_tests.py --help    # Show this help")
            return True
    
    # Run all tests by default
    return run_doctor_appointment_tests()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 