import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest

try:
    user, created = User.objects.get_or_create(
        username='testpatient3', 
        defaults={'email': 'test3@example.com'}
    )
    patient, created = Patient.objects.get_or_create(
        user=user, 
        defaults={'date_of_birth': '1990-01-01', 'gender': 'M'}
    )
    selftest = SelfTest.objects.create(
        patient=patient, 
        risk_level='low', 
        ai_recommendation='Test'
    )
    print(f'✅ Database test successful! SelfTest created with ID: {selftest.id}')
    print(f'✅ Patient field exists and works correctly')
except Exception as e:
    print(f'❌ Database test failed: {str(e)}') 