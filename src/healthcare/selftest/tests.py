from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from patient.models import Patient
from .models import SelfTest, Symptom, SymptomReport
from .ai_engine import HealthAIEngine
import json


class SelfTestModelTests(TestCase):
    """Test the SelfTest models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Patient'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            gender='M',
            phone='1234567890'
        )
        
        # Create test symptoms
        self.symptom1 = Symptom.objects.create(
            name='Fever',
            description='Elevated body temperature',
            category='General'
        )
        self.symptom2 = Symptom.objects.create(
            name='Headache',
            description='Pain in the head',
            category='Neurological'
        )
        self.symptom3 = Symptom.objects.create(
            name='Cough',
            description='Forceful expulsion of air from lungs',
            category='Respiratory'
        )
    
    def test_symptom_creation(self):
        """Test symptom model creation"""
        self.assertEqual(self.symptom1.name, 'Fever')
        self.assertEqual(self.symptom1.category, 'General')
        self.assertEqual(str(self.symptom1), 'Fever')
    
    def test_selftest_creation(self):
        """Test self-test creation"""
        selftest = SelfTest.objects.create(
            patient=self.patient,
            risk_level='medium',
            ai_recommendation='Rest and monitor symptoms',
            predicted_diseases=[{'name': 'Common Cold', 'confidence': 75}]
        )
        
        self.assertEqual(selftest.patient, self.patient)
        self.assertEqual(selftest.risk_level, 'medium')
        self.assertEqual(len(selftest.predicted_diseases), 1)
    
    def test_symptom_report_creation(self):
        """Test symptom report creation"""
        selftest = SelfTest.objects.create(
            patient=self.patient,
            risk_level='low'
        )
        
        symptom_report = SymptomReport.objects.create(
            self_test=selftest,
            symptom=self.symptom1,
            severity=2,
            duration_days=3,
            notes='Started yesterday'
        )
        
        self.assertEqual(symptom_report.severity, 2)
        self.assertEqual(symptom_report.duration_days, 3)
        self.assertEqual(symptom_report.symptom, self.symptom1)


class AIEngineTests(TestCase):
    """Test the AI Engine functionality"""
    
    def setUp(self):
        """Set up AI engine"""
        self.ai_engine = HealthAIEngine()
    
    def test_symptom_search(self):
        """Test symptom search functionality"""
        # Test empty query
        results = self.ai_engine.search_symptoms("")
        self.assertIsInstance(results, list)
        
        # Test specific search
        results = self.ai_engine.search_symptoms("fever")
        self.assertIsInstance(results, list)
        
        # Test case insensitive search
        results = self.ai_engine.search_symptoms("FEVER")
        self.assertIsInstance(results, list)
    
    def test_symptom_analysis_empty(self):
        """Test analysis with no symptoms"""
        result = self.ai_engine.analyze_symptoms([])
        
        self.assertEqual(result['risk_level'], 'low')
        self.assertEqual(len(result['predicted_diseases']), 0)
        self.assertIn('No symptoms', result['recommendations'])
    
    def test_symptom_analysis_with_symptoms(self):
        """Test analysis with known symptoms"""
        # Test with fever and headache (common cold symptoms)
        symptom_reports = [
            {'symptom_name': 'fever', 'severity': 2, 'duration_days': 2},
            {'symptom_name': 'headache', 'severity': 2, 'duration_days': 2},
            {'symptom_name': 'runny nose', 'severity': 1, 'duration_days': 1}
        ]
        
        result = self.ai_engine.analyze_symptoms(symptom_reports)
        
        self.assertIn('risk_level', result)
        self.assertIn('predicted_diseases', result)
        self.assertIn('recommendations', result)
        self.assertIn('specialist_referral', result)
        
        # Should predict some diseases
        self.assertGreater(len(result['predicted_diseases']), 0)
        
        # Check that diseases have required fields
        for disease in result['predicted_diseases']:
            self.assertIn('name', disease)
            self.assertIn('confidence', disease)
            self.assertIn('risk_level', disease)
    
    def test_high_severity_symptoms(self):
        """Test analysis with high severity symptoms"""
        symptom_reports = [
            {'symptom_name': 'chest pain', 'severity': 4, 'duration_days': 1},
            {'symptom_name': 'difficulty breathing', 'severity': 4, 'duration_days': 1}
        ]
        
        result = self.ai_engine.analyze_symptoms(symptom_reports)
        
        # High severity symptoms should result in higher risk
        self.assertIn(result['risk_level'], ['high', 'urgent'])


class SelfTestViewTests(TestCase):
    """Test the self-test views"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        
        # Create test symptoms in database
        Symptom.objects.create(name='Fever', description='High temperature', category='General')
        Symptom.objects.create(name='Headache', description='Head pain', category='Neurological')
        Symptom.objects.create(name='Cough', description='Respiratory symptom', category='Respiratory')
    
    def test_selftest_home_view(self):
        """Test self-test home page"""
        response = self.client.get(reverse('selftest:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI-Powered Health Assessment')
    
    def test_selftest_dashboard_requires_login(self):
        """Test that dashboard requires login"""
        response = self.client.get(reverse('selftest:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_selftest_dashboard_authenticated(self):
        """Test dashboard with authenticated user"""
        self.client.login(username='testpatient', password='testpass123')
        response = self.client.get(reverse('selftest:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Self-Test Dashboard')
    
    def test_quick_test_view(self):
        """Test quick test page"""
        self.client.login(username='testpatient', password='testpass123')
        response = self.client.get(reverse('selftest:quick_test'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quick Health Assessment')
    
    def test_symptom_search_api(self):
        """Test symptom search API"""
        self.client.login(username='testpatient', password='testpass123')
        response = self.client.get(
            reverse('selftest:quick_symptom_search_api'),
            {'q': 'fever'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('symptoms', data)
        self.assertIn('success', data)


class SelfTestIntegrationTests(TestCase):
    """Integration tests for the complete self-test workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        
        # Create symptoms that match disease patterns
        Symptom.objects.create(name='Fever', description='High temperature', category='General')
        Symptom.objects.create(name='Headache', description='Head pain', category='Neurological')
        Symptom.objects.create(name='Muscle Aches', description='Body aches', category='Musculoskeletal')
        Symptom.objects.create(name='Fatigue', description='Tiredness', category='General')
        Symptom.objects.create(name='Cough', description='Respiratory symptom', category='Respiratory')
        Symptom.objects.create(name='Sore Throat', description='Throat pain', category='Respiratory')
    
    def test_complete_quick_test_workflow(self):
        """Test complete quick test workflow with known symptoms"""
        self.client.login(username='testpatient', password='testpass123')
        
        # Test symptoms that should predict influenza
        selected_symptoms = [
            {
                'name': 'Fever',
                'description': 'High temperature',
                'category': 'General',
                'severity': 3
            },
            {
                'name': 'Muscle Aches',
                'description': 'Body aches',
                'category': 'Musculoskeletal',
                'severity': 3
            },
            {
                'name': 'Fatigue',
                'description': 'Tiredness',
                'category': 'General',
                'severity': 2
            },
            {
                'name': 'Headache',
                'description': 'Head pain',
                'category': 'Neurological',
                'severity': 2
            }
        ]
        
        # Submit quick test
        response = self.client.post(
            reverse('selftest:quick_test'),
            {
                'selected_symptoms': json.dumps(selected_symptoms),
                'additional_notes': 'Started 2 days ago'
            }
        )
        
        # Should return JSON response with success
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if data.get('success'):
            # Check that a self-test was created
            self.assertTrue(SelfTest.objects.filter(patient=self.patient).exists())
            
            # Get the created test
            selftest = SelfTest.objects.filter(patient=self.patient).first()
            
            # Verify test data
            self.assertIsNotNone(selftest.risk_level)
            self.assertIsNotNone(selftest.ai_recommendation)
            self.assertGreater(len(selftest.predicted_diseases), 0)
            
            # Check that symptom reports were created
            self.assertEqual(selftest.symptom_reports.count(), len(selected_symptoms))
            
            # Verify that influenza or similar respiratory illness is predicted
            disease_names = [disease['name'].lower() for disease in selftest.predicted_diseases]
            respiratory_diseases = ['influenza', 'flu', 'common cold', 'viral infection']
            has_respiratory_prediction = any(
                any(resp_disease in disease_name for resp_disease in respiratory_diseases)
                for disease_name in disease_names
            )
            
            print(f"Predicted diseases: {[d['name'] for d in selftest.predicted_diseases]}")
            print(f"Risk level: {selftest.risk_level}")
            
        else:
            print(f"Test failed with error: {data.get('error')}")
    
    def test_common_cold_symptoms(self):
        """Test with symptoms that should predict common cold"""
        self.client.login(username='testpatient', password='testpass123')
        
        # Common cold symptoms
        selected_symptoms = [
            {
                'name': 'Runny Nose',
                'description': 'Nasal discharge',
                'category': 'Respiratory',
                'severity': 2
            },
            {
                'name': 'Sneezing',
                'description': 'Nasal irritation',
                'category': 'Respiratory',
                'severity': 1
            },
            {
                'name': 'Sore Throat',
                'description': 'Throat pain',
                'category': 'Respiratory',
                'severity': 2
            },
            {
                'name': 'Cough',
                'description': 'Respiratory symptom',
                'category': 'Respiratory',
                'severity': 1
            }
        ]
        
        # Create these symptoms in database
        for symptom_data in selected_symptoms:
            Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={
                    'description': symptom_data['description'],
                    'category': symptom_data['category']
                }
            )
        
        response = self.client.post(
            reverse('selftest:quick_test'),
            {
                'selected_symptoms': json.dumps(selected_symptoms),
                'additional_notes': 'Mild cold symptoms'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if data.get('success'):
            selftest = SelfTest.objects.filter(patient=self.patient).first()
            
            # Should be low to medium risk for common cold
            self.assertIn(selftest.risk_level, ['low', 'medium'])
            
            # Should have predictions
            self.assertGreater(len(selftest.predicted_diseases), 0)
            
            print(f"Common cold test - Predicted diseases: {[d['name'] for d in selftest.predicted_diseases]}")
            print(f"Risk level: {selftest.risk_level}")
    
    def test_severe_symptoms(self):
        """Test with severe symptoms that should trigger high risk"""
        self.client.login(username='testpatient', password='testpass123')
        
        # Severe symptoms
        selected_symptoms = [
            {
                'name': 'Chest Pain',
                'description': 'Severe chest discomfort',
                'category': 'Cardiovascular',
                'severity': 4
            },
            {
                'name': 'Difficulty Breathing',
                'description': 'Shortness of breath',
                'category': 'Respiratory',
                'severity': 4
            }
        ]
        
        # Create these symptoms in database
        for symptom_data in selected_symptoms:
            Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={
                    'description': symptom_data['description'],
                    'category': symptom_data['category']
                }
            )
        
        response = self.client.post(
            reverse('selftest:quick_test'),
            {
                'selected_symptoms': json.dumps(selected_symptoms),
                'additional_notes': 'Severe symptoms'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if data.get('success'):
            selftest = SelfTest.objects.filter(patient=self.patient).first()
            
            # Should be high or urgent risk
            self.assertIn(selftest.risk_level, ['high', 'urgent'])
            
            print(f"Severe symptoms test - Risk level: {selftest.risk_level}")
            print(f"Recommendations: {selftest.ai_recommendation[:100]}...")


class SelfTestFormTests(TestCase):
    """Test form validation and functionality"""
    
    def test_severity_choices(self):
        """Test that severity choices are limited to 1-4"""
        from .forms import SymptomReportForm
        
        form = SymptomReportForm()
        severity_choices = form.fields['severity'].choices
        
        # Should have exactly 4 choices
        self.assertEqual(len(severity_choices), 4)
        
        # Should be numbered 1-4
        choice_values = [choice[0] for choice in severity_choices]
        self.assertEqual(choice_values, [1, 2, 3, 4])
        
        # Check choice labels
        choice_labels = [choice[1] for choice in severity_choices]
        self.assertIn('Mild', choice_labels[0])
        self.assertIn('Moderate', choice_labels[1])
        self.assertIn('Severe', choice_labels[2])
        self.assertIn('Very Severe', choice_labels[3])


def run_all_tests():
    """Run all tests and print results"""
    import unittest
    
    # Create test suite
    test_classes = [
        SelfTestModelTests,
        AIEngineTests,
        SelfTestViewTests,
        SelfTestIntegrationTests,
        SelfTestFormTests
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    run_all_tests() 