import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest

print("Testing SelfTest functionality...")

try:
    # Create test user
    user = User.objects.create_user(
        username='testpatient_final',
        email='final@example.com',
        password='test123'
    )
    print(f"✅ User created: {user}")
    
    # Create patient
    patient = Patient.objects.create(
        user=user,
        date_of_birth='1990-01-01',
        gender='M',
        phone='1234567890'
    )
    print(f"✅ Patient created: {patient}")
    
    # Create selftest
    selftest = SelfTest.objects.create(
        patient=patient,
        risk_level='low',
        ai_recommendation='Test recommendation'
    )
    print(f"✅ SelfTest created successfully!")
    print(f"   ID: {selftest.id}")
    print(f"   Patient: {selftest.patient}")
    print(f"   Risk Level: {selftest.risk_level}")
    print(f"   Created: {selftest.created_at}")
    
    print("\n🎉 SUCCESS: The patient_id issue is FIXED!")
    print("💡 The selftest functionality should now work without errors.")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc() 