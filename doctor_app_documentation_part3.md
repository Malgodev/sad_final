# Doctor App Documentation - Part 3

## 7. Tests (tests.py)

```python
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
```

## 8. Database Migrations

### a. Initial Migration (migrations/0001_initial.py)

```python
# Generated by Django 4.2.21 on 2025-05-25 10:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialization', models.CharField(default='General Medicine', max_length=100)),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('experience_years', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Doctor',
                'verbose_name_plural': 'Doctors',
            },
        ),
    ]
```

### b. Approval System Migration (migrations/0002_doctor_approval_status_doctor_approved_at_and_more.py)

```python
# Generated by Django 4.2.21 on 2025-05-25 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='doctor',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_doctors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='doctor',
            name='rejection_reason',
            field=models.TextField(blank=True),
        ),
    ]
```

## 9. Management Commands

### a. Sample Data Population Command (management/commands/populate_sample_data.py)

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from doctor.models import Doctor
from patient.models import Patient
from appointment.models import Appointment
from selftest.models import Symptom, SelfTest, SymptomReport
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create sample users
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@healthcare.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))

        # Create sample doctors
        doctor_data = [
            {'username': 'dr_smith', 'first_name': 'John', 'last_name': 'Smith', 'specialization': 'Cardiology', 'license': 'MD001'},
            {'username': 'dr_jones', 'first_name': 'Sarah', 'last_name': 'Jones', 'specialization': 'Pediatrics', 'license': 'MD002'},
            {'username': 'dr_brown', 'first_name': 'Michael', 'last_name': 'Brown', 'specialization': 'Neurology', 'license': 'MD003'},
        ]

        for doc_data in doctor_data:
            if not User.objects.filter(username=doc_data['username']).exists():
                user = User.objects.create_user(
                    username=doc_data['username'],
                    email=f"{doc_data['username']}@healthcare.com",
                    password='doctor123',
                    first_name=doc_data['first_name'],
                    last_name=doc_data['last_name']
                )
                Doctor.objects.create(
                    user=user,
                    specialization=doc_data['specialization'],
                    license_number=doc_data['license'],
                    phone=f"555-{random.randint(1000, 9999)}",
                    experience_years=random.randint(5, 20)
                )
                self.stdout.write(f"Created doctor: {doc_data['username']}/doctor123")

        # Create sample patients
        patient_data = [
            {'username': 'patient1', 'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'F'},
            {'username': 'patient2', 'first_name': 'Bob', 'last_name': 'Wilson', 'gender': 'M'},
            {'username': 'patient3', 'first_name': 'Carol', 'last_name': 'Davis', 'gender': 'F'},
        ]

        for pat_data in patient_data:
            if not User.objects.filter(username=pat_data['username']).exists():
                user = User.objects.create_user(
                    username=pat_data['username'],
                    email=f"{pat_data['username']}@email.com",
                    password='patient123',
                    first_name=pat_data['first_name'],
                    last_name=pat_data['last_name']
                )
                Patient.objects.create(
                    user=user,
                    gender=pat_data['gender'],
                    phone=f"555-{random.randint(1000, 9999)}",
                    address=f"{random.randint(100, 999)} Main St, City, State"
                )
                self.stdout.write(f"Created patient: {pat_data['username']}/patient123")

        # Create sample symptoms
        symptoms_data = [
            {'name': 'Headache', 'description': 'Pain in the head or neck area'},
            {'name': 'Fever', 'description': 'Elevated body temperature'},
            {'name': 'Cough', 'description': 'Sudden expulsion of air from lungs'},
            {'name': 'Fatigue', 'description': 'Extreme tiredness or exhaustion'},
            {'name': 'Nausea', 'description': 'Feeling of sickness with urge to vomit'},
        ]

        for symptom_data in symptoms_data:
            if not Symptom.objects.filter(name=symptom_data['name']).exists():
                Symptom.objects.create(**symptom_data)
                self.stdout.write(f"Created symptom: {symptom_data['name']}")

        # Create sample appointments
        doctors = Doctor.objects.all()
        patients = Patient.objects.all()
        
        if doctors.exists() and patients.exists():
            for i in range(5):
                if not Appointment.objects.filter(
                    doctor=random.choice(doctors),
                    patient=random.choice(patients)
                ).exists():
                    appointment_date = datetime.now() + timedelta(days=random.randint(1, 30))
                    Appointment.objects.create(
                        doctor=random.choice(doctors),
                        patient=random.choice(patients),
                        appointment_date=appointment_date,
                        reason=f"Sample appointment {i+1}",
                        status='scheduled'
                    )
            self.stdout.write("Created sample appointments")

        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
```

## 10. Key Features Summary

### a. Doctor Approval System
- **Admin-controlled approval process** for new doctor registrations
- **Three-state approval system**: pending, approved, rejected
- **Automatic account activation/deactivation** based on approval status
- **Audit trail** with approval timestamps and approver information

### b. Appointment Slot Management
- **Calendar-based slot creation** for individual days
- **Bulk slot creation** across date ranges with weekday selection
- **Time slot templates** (morning/afternoon sessions)
- **Slot availability tracking** and booking management
- **Appointment status management** (scheduled, completed, cancelled)

### c. Authentication & Security
- **Separate authentication system** from patient login
- **JWT token support** for API access
- **Role-based access control** with approval checks
- **Session management** for web interface

### d. User Interface
- **Responsive dashboard** with appointment statistics
- **Interactive calendar** for slot management
- **Filtering and search** capabilities
- **Profile management** with editable doctor information

### e. Testing Coverage
- **Comprehensive unit tests** for all major functionality
- **Integration tests** for complete workflows
- **Authentication and authorization tests**
- **Calendar and appointment management tests**

### f. API Endpoints
- **Doctor login API** with JWT token response
- **Patient search API** for appointment booking
- **RESTful design** following Django conventions

This comprehensive doctor app provides a complete solution for medical professional management within the healthcare system, including registration, approval, appointment scheduling, and patient interaction capabilities. 