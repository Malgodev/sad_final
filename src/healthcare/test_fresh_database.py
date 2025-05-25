import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.contrib.auth.models import User
from patient.models import Patient
from selftest.models import SelfTest, Symptom

print("🧪 Testing Fresh Database...")

try:
    # Create test user
    user = User.objects.create_user(
        username='testpatient_fresh',
        email='fresh@example.com',
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
    
    # Test creating selftest with patient field
    selftest = SelfTest.objects.create(
        patient=patient,  # This should work with the fresh database
        risk_level='low',
        ai_recommendation='Fresh database test'
    )
    print(f"✅ SelfTest created successfully!")
    print(f"   ID: {selftest.id}")
    print(f"   Patient: {selftest.patient}")
    print(f"   Patient ID: {selftest.patient.id}")
    print(f"   Risk Level: {selftest.risk_level}")
    
    # Check if symptoms exist
    symptom_count = Symptom.objects.count()
    print(f"✅ Symptoms in database: {symptom_count}")
    
    print("\n🎉 SUCCESS: Fresh database is working correctly!")
    print("💡 The patient_id error should be completely resolved now.")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc() 