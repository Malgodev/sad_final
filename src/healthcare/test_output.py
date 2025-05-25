import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest

# Write output to file
with open('test_results.txt', 'w') as f:
    f.write("Testing database...\n")
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='testoutput',
            email='output@example.com',
            password='test123'
        )
        f.write(f"User created: {user}\n")
        
        # Create patient
        patient = Patient.objects.create(
            user=user,
            date_of_birth='1990-01-01',
            gender='M',
            phone='1234567890'
        )
        f.write(f"Patient created: {patient}\n")
        
        # Create selftest
        selftest = SelfTest.objects.create(
            patient=patient,
            risk_level='low',
            ai_recommendation='Test recommendation'
        )
        f.write(f"SelfTest created successfully!\n")
        f.write(f"ID: {selftest.id}\n")
        f.write(f"Patient: {selftest.patient}\n")
        f.write(f"SUCCESS: Database is working!\n")
        
    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
        import traceback
        f.write(traceback.format_exc())

print("Test completed. Check test_results.txt for output.") 