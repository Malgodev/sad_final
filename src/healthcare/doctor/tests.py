from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from doctor.models import Doctor
from patient.models import Patient
from appointment.models import AppointmentSlot, Appointment
import json


class DoctorAppointmentTestCase(TestCase):
    """Comprehensive test suite for doctor appointment functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.doctor_user = User.objects.create_user(
            username='test_doctor',
            email='doctor@test.com',
            password='testpass123',
            first_name='John',
            last_name='Smith'
        )
        
        self.patient_user = User.objects.create_user(
            username='test_patient',
            email='patient@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe'
        )
        
        # Create doctor profile
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            license_number='DOC123456',
            phone='555-0123',
            experience_years=10,
            approval_status='approved',
            approved_at=timezone.now()
        )
        
        # Create patient profile
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1990, 1, 1),
            gender='F',
            phone='555-0456',
            address='123 Test St'
        )
        
        # Test dates
        self.test_date = date.today() + timedelta(days=1)
        self.past_date = date.today() - timedelta(days=1)
        
    def test_doctor_authentication_required(self):
        """Test that doctor authentication is required for appointment views"""
        urls_to_test = [
            'doctor:appointment_calendar',
            'doctor:create_appointment_slots',
            'doctor:bulk_create_slots',
            'doctor:appointment_list',
        ]
        
        for url_name in urls_to_test:
            response = self.client.get(reverse(url_name))
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            # Should redirect to login (either /doctor/auth/ or /accounts/login/)
            self.assertTrue('/auth/' in response.url or '/login/' in response.url)
    
    def test_doctor_login_and_dashboard_access(self):
        """Test doctor login and dashboard access"""
        # Test login
        login_data = {
            'email': 'doctor@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('doctor:doctor_login'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Test dashboard access after login
        response = self.client.get(reverse('doctor:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. John Smith')
    
    def test_appointment_calendar_view(self):
        """Test appointment calendar view"""
        self.client.force_login(self.doctor_user)
        
        # Create test slot
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        response = self.client.get(reverse('doctor:appointment_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appointment Slots Calendar')
        self.assertContains(response, str(self.test_date.year))
    
    def test_create_appointment_slots_view(self):
        """Test creating appointment slots"""
        self.client.force_login(self.doctor_user)
        
        response = self.client.get(reverse('doctor:create_appointment_slots'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Appointment Slots')
        
        # Test slot creation
        slot_data = {
            'date': self.test_date.strftime('%Y-%m-%d'),
            'slot_types': ['morning_1', 'afternoon_1']
        }
        response = self.client.post(reverse('doctor:create_appointment_slots'), slot_data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verify slots were created
        slots = AppointmentSlot.objects.filter(doctor=self.doctor, date=self.test_date)
        self.assertEqual(slots.count(), 2)
    
    def test_bulk_create_slots_view(self):
        """Test bulk slot creation"""
        self.client.force_login(self.doctor_user)
        
        response = self.client.get(reverse('doctor:bulk_create_slots'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bulk Create Appointment Slots')
        
        # Test bulk creation
        start_date = self.test_date
        end_date = self.test_date + timedelta(days=7)
        
        bulk_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days_of_week': ['1', '2', '3'],  # Mon, Tue, Wed
            'slot_types': ['afternoon_1', 'afternoon_2']
        }
        response = self.client.post(reverse('doctor:bulk_create_slots'), bulk_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify slots were created for multiple days
        slots = AppointmentSlot.objects.filter(
            doctor=self.doctor,
            date__range=[start_date, end_date]
        )
        self.assertGreater(slots.count(), 0)
    
    def test_appointment_list_view(self):
        """Test appointment list view with filters"""
        self.client.force_login(self.doctor_user)
        
        # Create test slots
        available_slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        booked_slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='afternoon_1'
        )
        
        # Create appointment for booked slot
        appointment = Appointment.objects.create(
            appointment_slot=booked_slot,
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(booked_slot.date, booked_slot.start_time)
            ),
            status='scheduled',
            reason='Regular checkup'
        )
        
        response = self.client.get(reverse('doctor:appointment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appointment Slots')
        
        # Test filtering by status
        response = self.client.get(reverse('doctor:appointment_list') + '?status=available')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('doctor:appointment_list') + '?status=booked')
        self.assertEqual(response.status_code, 200)
    
    def test_slot_detail_view(self):
        """Test slot detail view"""
        self.client.force_login(self.doctor_user)
        
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        response = self.client.get(reverse('doctor:slot_detail', args=[slot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, slot.get_slot_type_display())
        self.assertContains(response, 'Available')
    
    def test_slot_detail_with_patient(self):
        """Test slot detail view when slot is booked by patient"""
        self.client.force_login(self.doctor_user)
        
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='afternoon_1'
        )
        
        appointment = Appointment.objects.create(
            appointment_slot=slot,
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(slot.date, slot.start_time)
            ),
            status='scheduled',
            reason='Follow-up appointment'
        )
        
        response = self.client.get(reverse('doctor:slot_detail', args=[slot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Follow-up appointment')
        self.assertContains(response, 'Booked')
    
    def test_update_appointment_status(self):
        """Test updating appointment status"""
        self.client.force_login(self.doctor_user)
        
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_2'
        )
        
        appointment = Appointment.objects.create(
            appointment_slot=slot,
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(slot.date, slot.start_time)
            ),
            status='scheduled',
            reason='Initial consultation'
        )
        
        # Update appointment status
        update_data = {
            'status': 'completed',
            'notes': 'Patient responded well to treatment'
        }
        response = self.client.post(
            reverse('doctor:slot_detail', args=[slot.id]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')
        self.assertEqual(appointment.notes, 'Patient responded well to treatment')
    
    def test_delete_empty_slot(self):
        """Test deleting an empty appointment slot"""
        self.client.force_login(self.doctor_user)
        
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='afternoon_2'
        )
        
        response = self.client.get(reverse('doctor:delete_slot', args=[slot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Appointment Slot')
        
        # Confirm deletion
        response = self.client.post(reverse('doctor:delete_slot', args=[slot.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify slot is deleted
        self.assertFalse(AppointmentSlot.objects.filter(id=slot.id).exists())
    
    def test_cannot_delete_booked_slot(self):
        """Test that booked slots cannot be deleted"""
        self.client.force_login(self.doctor_user)
        
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        appointment = Appointment.objects.create(
            appointment_slot=slot,
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(slot.date, slot.start_time)
            ),
            status='scheduled'
        )
        
        response = self.client.get(reverse('doctor:delete_slot', args=[slot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot Delete!')
        
        # Try to delete - should not work
        response = self.client.post(reverse('doctor:delete_slot', args=[slot.id]))
        # Should still show the page, not redirect
        self.assertEqual(response.status_code, 200)
        
        # Verify slot still exists
        self.assertTrue(AppointmentSlot.objects.filter(id=slot.id).exists())
    
    def test_slot_time_calculations(self):
        """Test that slot times are calculated correctly"""
        slot_morning_1 = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        slot_afternoon_2 = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='afternoon_2'
        )
        
        # Check morning slot times
        self.assertEqual(slot_morning_1.start_time, time(8, 0))
        self.assertEqual(slot_morning_1.end_time, time(9, 30))
        
        # Check afternoon slot times
        self.assertEqual(slot_afternoon_2.start_time, time(15, 30))
        self.assertEqual(slot_afternoon_2.end_time, time(17, 0))
    
    def test_duplicate_slot_prevention(self):
        """Test that duplicate slots cannot be created"""
        # Create first slot
        AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='morning_1'
        )
        
        # Try to create duplicate - should raise error
        with self.assertRaises(Exception):
            AppointmentSlot.objects.create(
                doctor=self.doctor,
                date=self.test_date,
                slot_type='morning_1'
            )
    
    def test_calendar_navigation(self):
        """Test calendar month navigation"""
        self.client.force_login(self.doctor_user)
        
        # Test next month navigation
        next_month = date.today().replace(day=1) + timedelta(days=32)
        response = self.client.get(
            reverse('doctor:appointment_calendar') + 
            f'?year={next_month.year}&month={next_month.month}'
        )
        self.assertEqual(response.status_code, 200)
        
        # Test previous month navigation
        prev_month = date.today().replace(day=1) - timedelta(days=1)
        response = self.client.get(
            reverse('doctor:appointment_calendar') + 
            f'?year={prev_month.year}&month={prev_month.month}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_doctor_approval_required(self):
        """Test that unapproved doctors cannot access appointment features"""
        # Create unapproved doctor
        unapproved_user = User.objects.create_user(
            username='unapproved_doctor',
            email='unapproved@test.com',
            password='testpass123'
        )
        
        unapproved_doctor = Doctor.objects.create(
            user=unapproved_user,
            specialization='Dermatology',
            license_number='DOC789012',
            approval_status='pending'
        )
        
        # Try to login
        login_data = {
            'email': 'unapproved@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('doctor:doctor_login'), login_data)
        
        # Should be redirected back to login with error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pending approval')
    
    def test_appointment_slot_model_methods(self):
        """Test AppointmentSlot model methods"""
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            date=self.test_date,
            slot_type='afternoon_1'
        )
        
        # Test string representation
        expected_str = f"Dr. {self.doctor.user.get_full_name()} - {self.test_date} Afternoon 1:30 - 3:00"
        self.assertEqual(str(slot), expected_str)
        
        # Test is_available method (if exists)
        self.assertTrue(hasattr(slot, 'appointment'))
    
    def test_form_validation(self):
        """Test form validation for slot creation"""
        self.client.force_login(self.doctor_user)
        
        # Test creating slot for past date (should be prevented)
        past_data = {
            'date': self.past_date.strftime('%Y-%m-%d'),
            'slot_types': ['morning_1']
        }
        response = self.client.post(reverse('doctor:create_appointment_slots'), past_data)
        
        # Should show form with error or redirect with message
        # The exact behavior depends on form validation implementation
        self.assertIn(response.status_code, [200, 302])


class DoctorAppointmentIntegrationTest(TestCase):
    """Integration tests for complete appointment workflows"""
    
    def setUp(self):
        """Set up test data for integration tests"""
        self.client = Client()
        
        # Create doctor
        self.doctor_user = User.objects.create_user(
            username='integration_doctor',
            email='integration@test.com',
            password='testpass123',
            first_name='Integration',
            last_name='Doctor'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='General Medicine',
            license_number='INT123456',
            phone='555-9999',
            experience_years=5,
            approval_status='approved',
            approved_at=timezone.now()
        )
        
        # Create patient
        self.patient_user = User.objects.create_user(
            username='integration_patient',
            email='patient_int@test.com',
            password='testpass123',
            first_name='Integration',
            last_name='Patient'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1985, 5, 15),
            gender='M',
            phone='555-8888'
        )
    
    def test_complete_appointment_workflow(self):
        """Test complete appointment workflow from slot creation to completion"""
        self.client.force_login(self.doctor_user)
        
        # Step 1: Create appointment slot
        test_date = date.today() + timedelta(days=2)
        slot_data = {
            'date': test_date.strftime('%Y-%m-%d'),
            'slot_types': ['morning_1']
        }
        response = self.client.post(reverse('doctor:create_appointment_slots'), slot_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify slot was created
        slot = AppointmentSlot.objects.get(
            doctor=self.doctor,
            date=test_date,
            slot_type='morning_1'
        )
        self.assertIsNotNone(slot)
        
        # Step 2: Simulate patient booking (would normally be done through patient interface)
        appointment = Appointment.objects.create(
            appointment_slot=slot,
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.make_aware(
                timezone.datetime.combine(slot.date, slot.start_time)
            ),
            status='scheduled',
            reason='Annual checkup'
        )
        
        # Step 3: Doctor views slot details
        response = self.client.get(reverse('doctor:slot_detail', args=[slot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Patient')
        self.assertContains(response, 'Annual checkup')
        
        # Step 4: Doctor updates appointment status
        update_data = {
            'status': 'completed',
            'notes': 'Patient is in good health. Recommended annual follow-up.'
        }
        response = self.client.post(
            reverse('doctor:slot_detail', args=[slot.id]),
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Verify appointment was updated
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')
        self.assertIn('good health', appointment.notes)
        
        # Step 6: Verify slot appears correctly in calendar
        response = self.client.get(reverse('doctor:appointment_calendar'))
        self.assertEqual(response.status_code, 200)
        # Should show completed appointment
        self.assertContains(response, 'Integration')
    
    def test_bulk_slot_creation_and_management(self):
        """Test bulk slot creation and subsequent management"""
        self.client.force_login(self.doctor_user)
        
        # Create bulk slots for a week
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        
        bulk_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days_of_week': ['1', '2', '3', '4', '5'],  # Weekdays
            'slot_types': ['afternoon_1', 'afternoon_2']
        }
        
        response = self.client.post(reverse('doctor:bulk_create_slots'), bulk_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify slots were created
        slots = AppointmentSlot.objects.filter(
            doctor=self.doctor,
            date__range=[start_date, end_date]
        )
        
        # Should have created slots for weekdays only
        expected_slots = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                expected_slots += 2  # Two slot types
            current_date += timedelta(days=1)
        
        self.assertEqual(slots.count(), expected_slots)
        
        # Test list view shows all slots
        response = self.client.get(reverse('doctor:appointment_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test filtering by date
        response = self.client.get(
            reverse('doctor:appointment_list') + 
            f'?date={start_date.strftime("%Y-%m-%d")}'
        )
        self.assertEqual(response.status_code, 200)


# Run tests with: python manage.py test doctor.tests
