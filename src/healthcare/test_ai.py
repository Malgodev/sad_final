#!/usr/bin/env python
"""
Test script for the enhanced AI engine with ML models
"""
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from selftest.ai_engine import HealthAIEngine


def test_ai_engine():
    """Test the AI engine with sample symptoms"""
    print("🤖 Testing Enhanced AI Engine with ML Models")
    print("=" * 50)
    
    # Initialize AI engine
    ai_engine = HealthAIEngine()
    
    # Test cases
    test_cases = [
        {
            'name': 'Flu-like symptoms',
            'symptoms': [
                {'symptom_name': 'Fever', 'severity': 3, 'duration_days': 2},
                {'symptom_name': 'Headache', 'severity': 2, 'duration_days': 2},
                {'symptom_name': 'Muscle Aches', 'severity': 3, 'duration_days': 2},
                {'symptom_name': 'Fatigue', 'severity': 4, 'duration_days': 3}
            ]
        },
        {
            'name': 'Respiratory symptoms',
            'symptoms': [
                {'symptom_name': 'Cough', 'severity': 3, 'duration_days': 5},
                {'symptom_name': 'Difficulty Breathing', 'severity': 2, 'duration_days': 3},
                {'symptom_name': 'Chest Pain', 'severity': 2, 'duration_days': 2}
            ]
        },
        {
            'name': 'Digestive symptoms',
            'symptoms': [
                {'symptom_name': 'Nausea', 'severity': 3, 'duration_days': 1},
                {'symptom_name': 'Vomiting', 'severity': 2, 'duration_days': 1},
                {'symptom_name': 'Stomach Pain', 'severity': 3, 'duration_days': 2}
            ]
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        
        # Print input symptoms
        print("Input symptoms:")
        for symptom in test_case['symptoms']:
            print(f"  • {symptom['symptom_name']}: Severity {symptom['severity']}/4, {symptom['duration_days']} days")
        
        # Get AI prediction
        try:
            result = ai_engine.analyze_symptoms(test_case['symptoms'])
            
            print(f"\n🎯 AI Prediction Results:")
            print(f"   Risk Level: {result.get('risk_level', 'N/A').upper()}")
            print(f"   ML Confidence: {result.get('ml_confidence', 0)}%")
            print(f"   Model Used: {result.get('model_used', 'N/A')}")
            
            predicted_diseases = result.get('predicted_diseases', [])
            if predicted_diseases:
                top_disease = predicted_diseases[0]
                print(f"   Top Prediction: {top_disease['name']} ({top_disease['confidence']}% confidence)")
                print(f"   Specialist: {top_disease.get('specialist', 'N/A')}")
            
            # Show all model predictions if available
            all_predictions = result.get('all_predictions', {})
            if all_predictions:
                print(f"\n📊 Individual Model Predictions:")
                for model, pred in all_predictions.items():
                    print(f"   {model}: {pred['disease']} ({pred['confidence']}%)")
            
            print(f"\n💡 Recommendations: {result.get('recommendations', 'N/A')[:100]}...")
            
        except Exception as e:
            print(f"❌ Error in prediction: {str(e)}")
    
    # Test model comparison
    print(f"\n📈 Model Performance Comparison:")
    print("-" * 30)
    comparison = ai_engine.get_model_comparison()
    if comparison:
        for model_name, metrics in comparison.items():
            print(f"{model_name}: {metrics['test_accuracy']:.3f} accuracy ({metrics['status']})")
    else:
        print("No model comparison data available")
    
    print(f"\n✅ AI Engine Test Completed!")


if __name__ == "__main__":
    test_ai_engine() 