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