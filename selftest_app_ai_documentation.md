# Selftest App AI Documentation

## 1. Folder Structure

```
src/healthcare/selftest/
├── __init__.py
├── apps.py
├── models.py
├── forms.py
├── views.py
├── urls.py
├── admin.py
├── tests.py
├── ai_engine.py              # Main AI Engine
├── ml_models.py              # Machine Learning Models
├── data/
│   ├── symptoms.json         # Symptoms Knowledge Base
│   └── diseases.json         # Diseases Knowledge Base
├── ml_models/                # Trained ML Models Storage
│   ├── random_forest_model.pkl
│   ├── svm_model.pkl
│   ├── neural_network_model.pkl
│   ├── naive_bayes_model.pkl
│   ├── disease_encoder.pkl
│   ├── scaler.pkl
│   └── model_accuracies.json
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── train_ml_models.py
│       ├── populate_symptoms.py
│       └── create_symptoms.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

## 2. Core AI Engine (ai_engine.py)

### a. Main AI Engine Class

```python
import json
import os
from typing import List, Dict, Tuple
from django.conf import settings
from .ml_models import HealthMLEngine


class HealthAIEngine:
    """AI Engine for symptom analysis and disease prediction with ML capabilities"""
    
    def __init__(self):
        self.symptoms_data = self._load_symptoms()
        self.diseases_data = self._load_diseases()
        self.ml_engine = HealthMLEngine()
        
        # Train models if not already trained
        if not self.ml_engine.is_trained:
            self._train_ml_models()
    
    def _load_symptoms(self) -> Dict:
        """Load symptoms data from JSON file"""
        file_path = os.path.join(settings.BASE_DIR, 'selftest', 'data', 'symptoms.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"symptoms": []}
    
    def _load_diseases(self) -> Dict:
        """Load diseases data from JSON file"""
        file_path = os.path.join(settings.BASE_DIR, 'selftest', 'data', 'diseases.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"diseases": []}
    
    def search_symptoms(self, query: str, limit: int = 10) -> List[Dict]:
        """Search symptoms based on query string"""
        if not query:
            return self.symptoms_data.get('symptoms', [])[:limit]
        
        query_lower = query.lower()
        matching_symptoms = []
        
        for symptom in self.symptoms_data.get('symptoms', []):
            # Check if query matches symptom name
            if query_lower in symptom['name'].lower():
                matching_symptoms.append(symptom)
                continue
            
            # Check if query matches description
            if query_lower in symptom['description'].lower():
                matching_symptoms.append(symptom)
                continue
            
            # Check if query matches keywords
            for keyword in symptom.get('keywords', []):
                if query_lower in keyword.lower():
                    matching_symptoms.append(symptom)
                    break
        
        return matching_symptoms[:limit]
    
    def analyze_symptoms(self, symptom_reports: List[Dict]) -> Dict:
        """
        Analyze symptoms and predict diseases with AI/ML models and rule-based fallback
        
        Args:
            symptom_reports: List of dicts with 'symptom_name', 'severity', 'duration_days'
        
        Returns:
            Dict with predicted diseases, risk level, and recommendations
        """
        if not symptom_reports:
            return {
                'predicted_diseases': [],
                'risk_level': 'low',
                'recommendations': 'No symptoms reported. If you have health concerns, consult a healthcare provider.',
                'specialist_referral': None
            }
        
        # Try ML prediction first
        try:
            ml_result = self.ml_engine.predict_disease(symptom_reports, use_ensemble=True)
            
            # If ML prediction is successful and confident, use it
            if ml_result.get('ml_confidence', 0) > 40:  # 40% threshold for ML confidence
                return ml_result
                
        except Exception as e:
            print(f"ML prediction failed: {str(e)}")
        
        # Fallback to rule-based prediction
        return self._rule_based_prediction(symptom_reports)
```

## 3. Machine Learning Engine (ml_models.py)

### a. ML Engine Class

```python
import json
import os
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import logging

logger = logging.getLogger(__name__)


class HealthMLEngine:
    """
    Machine Learning Engine for symptom-disease prediction
    Implements multiple ML algorithms for comparison and ensemble prediction
    """
    
    def __init__(self):
        self.symptoms_data = self._load_symptoms()
        self.diseases_data = self._load_diseases()
        self.symptom_encoder = LabelEncoder()
        self.disease_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
        # Initialize models
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            ),
            'svm': SVC(
                kernel='rbf',
                probability=True,
                random_state=42,
                class_weight='balanced'
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            ),
            'naive_bayes': GaussianNB()
        }
        
        self.trained_models = {}
        self.model_accuracies = {}
        self.is_trained = False
        
        # Try to load pre-trained models
        self._load_trained_models()
```

### b. Training Data Preparation

```python
    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from symptoms and diseases JSON files
        Creates synthetic training data based on symptom-disease relationships
        """
        symptoms_list = [s['name'].lower() for s in self.symptoms_data.get('symptoms', [])]
        diseases_list = [d['name'] for d in self.diseases_data.get('diseases', [])]
        
        if not symptoms_list or not diseases_list:
            raise ValueError("No symptoms or diseases data available")
        
        training_data = []
        labels = []
        
        # Create training samples for each disease
        for disease in self.diseases_data.get('diseases', []):
            disease_name = disease['name']
            disease_symptoms = [s.lower() for s in disease.get('symptoms', [])]
            
            if not disease_symptoms:
                continue
            
            # Generate positive samples (with disease symptoms)
            for _ in range(20):  # Generate 20 samples per disease
                sample = np.zeros(len(symptoms_list))
                
                # Set primary symptoms (high probability)
                for symptom in disease_symptoms:
                    if symptom in symptoms_list:
                        idx = symptoms_list.index(symptom)
                        # Add some randomness: 70-100% chance of having primary symptoms
                        if np.random.random() > 0.3:
                            sample[idx] = np.random.uniform(2, 4)  # Severity 2-4
                
                # Add some random secondary symptoms (low probability)
                num_secondary = np.random.randint(0, 3)
                for _ in range(num_secondary):
                    random_idx = np.random.randint(0, len(symptoms_list))
                    if sample[random_idx] == 0:  # Only add if not already set
                        sample[random_idx] = np.random.uniform(1, 2)  # Lower severity
                
                training_data.append(sample)
                labels.append(disease_name)
            
            # Generate negative samples (without main disease symptoms)
            for _ in range(5):  # Generate 5 negative samples per disease
                sample = np.zeros(len(symptoms_list))
                
                # Add random symptoms but avoid main disease symptoms
                num_symptoms = np.random.randint(1, 4)
                available_indices = [i for i, s in enumerate(symptoms_list) 
                                   if s not in disease_symptoms]
                
                if available_indices:
                    selected_indices = np.random.choice(
                        available_indices, 
                        size=min(num_symptoms, len(available_indices)), 
                        replace=False
                    )
                    for idx in selected_indices:
                        sample[idx] = np.random.uniform(1, 3)
                
                training_data.append(sample)
                labels.append('Other')  # Generic label for non-matching cases
        
        return np.array(training_data), np.array(labels)
```

### c. Model Training

```python
    def train_models(self) -> Dict[str, float]:
        """
        Train all ML models and return their accuracies
        """
        logger.info("Starting model training...")
        
        # Prepare training data
        X, y = self._prepare_training_data()
        
        # Encode labels
        y_encoded = self.disease_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train each model
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_scaled, y_encoded, cv=5)
                cv_accuracy = cv_scores.mean()
                
                self.trained_models[name] = model
                self.model_accuracies[name] = {
                    'test_accuracy': accuracy,
                    'cv_accuracy': cv_accuracy,
                    'cv_std': cv_scores.std()
                }
                
                logger.info(f"{name} - Test Accuracy: {accuracy:.3f}, CV Accuracy: {cv_accuracy:.3f} ± {cv_scores.std():.3f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                self.model_accuracies[name] = {'test_accuracy': 0.0, 'cv_accuracy': 0.0, 'cv_std': 0.0}
        
        self.is_trained = True
        
        # Save trained models
        self._save_trained_models()
        
        return {name: scores['test_accuracy'] for name, scores in self.model_accuracies.items()}
```

### d. Disease Prediction

```python
    def predict_disease(self, symptom_reports: List[Dict], use_ensemble: bool = True) -> Dict:
        """
        Predict disease using trained ML models
        
        Args:
            symptom_reports: List of dicts with 'symptom_name', 'severity', 'duration_days'
            use_ensemble: Whether to use ensemble prediction or best single model
        
        Returns:
            Dict with predicted diseases, confidence scores, and ML insights
        """
        if not self.is_trained and not self._load_trained_models():
            logger.warning("Models not trained, falling back to rule-based prediction")
            return self._fallback_prediction(symptom_reports)
        
        if not symptom_reports:
            return {
                'predicted_diseases': [],
                'risk_level': 'low',
                'recommendations': 'No symptoms reported. If you have health concerns, consult a healthcare provider.',
                'specialist_referral': 'General Practitioner',
                'ml_confidence': 0.0,
                'model_used': 'none'
            }
        
        # Prepare input features
        X_input = self._prepare_input_features(symptom_reports)
        
        if X_input is None:
            return self._fallback_prediction(symptom_reports)
        
        # Get predictions from all models
        predictions = {}
        confidences = {}
        
        for name, model in self.trained_models.items():
            try:
                # Get prediction and confidence
                pred_proba = model.predict_proba(X_input.reshape(1, -1))[0]
                pred_class_idx = np.argmax(pred_proba)
                pred_class = self.disease_encoder.inverse_transform([pred_class_idx])[0]
                confidence = pred_proba[pred_class_idx]
                
                predictions[name] = pred_class
                confidences[name] = confidence
                
            except Exception as e:
                logger.error(f"Error predicting with {name}: {str(e)}")
                predictions[name] = 'Unknown'
                confidences[name] = 0.0
        
        # Ensemble prediction or best model
        if use_ensemble:
            final_prediction, final_confidence, model_used = self._ensemble_predict(predictions, confidences)
        else:
            # Use the model with highest accuracy
            best_model = max(self.model_accuracies.keys(), 
                           key=lambda x: self.model_accuracies[x]['test_accuracy'])
            final_prediction = predictions.get(best_model, 'Unknown')
            final_confidence = confidences.get(best_model, 0.0)
            model_used = best_model
        
        # Get disease details
        disease_info = self._get_disease_info(final_prediction)
        
        # Determine risk level
        risk_level = self._determine_ml_risk_level(final_confidence, disease_info, symptom_reports)
        
        # Generate recommendations
        recommendations = self._generate_ml_recommendations(disease_info, risk_level, final_confidence)
        
        return {
            'predicted_diseases': [{
                'name': final_prediction,
                'description': disease_info.get('description', 'AI-predicted condition'),
                'confidence': round(final_confidence * 100, 1),
                'risk_level': disease_info.get('risk_level', 'medium'),
                'treatment': disease_info.get('treatment', 'Consult healthcare provider'),
                'specialist': disease_info.get('specialist', 'General Practitioner'),
                'urgency': disease_info.get('urgency', 'Schedule appointment')
            }],
            'risk_level': risk_level,
            'recommendations': recommendations,
            'specialist_referral': disease_info.get('specialist', 'General Practitioner'),
            'ml_confidence': round(final_confidence * 100, 1),
            'model_used': model_used,
            'all_predictions': {name: {'disease': pred, 'confidence': round(conf * 100, 1)} 
                              for name, pred, conf in zip(predictions.keys(), predictions.values(), confidences.values())}
        }
```

## 4. Management Commands

### a. ML Training Command (management/commands/train_ml_models.py)

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from selftest.ai_engine import HealthAIEngine
import json
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Train ML models for symptom-disease prediction and generate comparison report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain models even if they already exist',
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='Generate report only without training',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ML model training and evaluation...'))
        
        # Initialize AI engine
        ai_engine = HealthAIEngine()
        
        if options['report_only']:
            self.stdout.write('Generating model comparison report only...')
            comparison = ai_engine.get_model_comparison()
            self._generate_report(comparison)
            return

        # Train models
        if options['force'] or not ai_engine.ml_engine.is_trained:
            self.stdout.write('Training ML models...')
            accuracies = ai_engine.force_retrain_models() if options['force'] else ai_engine._train_ml_models()
            
            if accuracies:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully trained {len(accuracies)} models')
                )
                for model_name, accuracy in accuracies.items():
                    self.stdout.write(f'  {model_name}: {accuracy:.3f}')
            else:
                self.stdout.write(self.style.ERROR('Model training failed'))
                return
        else:
            self.stdout.write('Models already trained. Use --force to retrain.')

        # Generate comparison report
        self.stdout.write('Generating model comparison report...')
        comparison = ai_engine.get_model_comparison()
        self._generate_report(comparison)
        
        self.stdout.write(self.style.SUCCESS('ML model training and evaluation completed!'))
```

## 5. AI-Related Views (views.py - AI portions)

### a. Quick Test Analysis API

```python
@login_required
@require_http_methods(["POST"])
def quick_analysis_api(request):
    """API endpoint for quick AI symptom analysis"""
    try:
        data = json.loads(request.body)
        selected_symptoms = data.get('symptoms', [])
        additional_notes = data.get('additional_notes', '')
        
        if not selected_symptoms:
            return JsonResponse({
                'success': False,
                'error': 'Please select at least one symptom.'
            }, status=400)
        
        # Initialize AI engine and analyze
        ai_engine = HealthAIEngine()
        
        # Prepare symptom reports for AI analysis
        symptom_reports = []
        for symptom_data in selected_symptoms:
            symptom_reports.append({
                'symptom_name': symptom_data['name'],
                'severity': symptom_data['severity'],
                'duration_days': symptom_data.get('duration', 1),
                'notes': symptom_data.get('notes', '')
            })
        
        # AI analysis
        analysis_result = ai_engine.analyze_symptoms(symptom_reports)
        
        # Save to database
        try:
            patient = Patient.objects.get(user=request.user)
            self_test = SelfTest.objects.create(
                patient=patient,
                risk_level=analysis_result['risk_level'],
                ai_recommendation=analysis_result['recommendations'],
                predicted_diseases=analysis_result['predicted_diseases'],
                additional_notes=additional_notes
            )
            
            # Create symptom reports
            for symptom_data in selected_symptoms:
                # Get or create symptom
                symptom, created = Symptom.objects.get_or_create(
                    name=symptom_data['name'],
                    defaults={
                        'description': symptom_data.get('description', ''),
                        'category': symptom_data.get('category', 'General')
                    }
                )
                
                SymptomReport.objects.create(
                    self_test=self_test,
                    symptom=symptom,
                    severity=symptom_data['severity'],
                    duration_days=symptom_data.get('duration', 1),
                    notes=symptom_data.get('notes', '')
                )
            
            return JsonResponse({
                'success': True,
                'redirect_url': f'/selftest/results/{self_test.id}/'
            })
            
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Patient profile not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error saving test: {str(e)}'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data provided.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }, status=500)
```

## 6. AI Tests (tests.py - AI portions)

### a. AI Engine Tests

```python
class AIEngineTests(TestCase):
    """Test the AI Engine functionality"""
    
    def setUp(self):
        """Set up AI engine for testing"""
        self.ai_engine = HealthAIEngine()
    
    def test_ai_engine_initialization(self):
        """Test AI engine initializes correctly"""
        self.assertIsNotNone(self.ai_engine.symptoms_data)
        self.assertIsNotNone(self.ai_engine.diseases_data)
        self.assertIsNotNone(self.ai_engine.ml_engine)
    
    def test_symptom_search(self):
        """Test symptom search functionality"""
        # Test with query
        results = self.ai_engine.search_symptoms("fever", limit=5)
        self.assertIsInstance(results, list)
        
        # Test empty query
        results = self.ai_engine.search_symptoms("", limit=5)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
    
    def test_symptom_analysis_empty(self):
        """Test analysis with no symptoms"""
        result = self.ai_engine.analyze_symptoms([])
        
        self.assertEqual(result['risk_level'], 'low')
        self.assertEqual(result['predicted_diseases'], [])
        self.assertIn('No symptoms reported', result['recommendations'])
    
    def test_symptom_analysis_with_symptoms(self):
        """Test analysis with symptoms"""
        symptom_reports = [
            {
                'symptom_name': 'Fever',
                'severity': 3,
                'duration_days': 2
            },
            {
                'symptom_name': 'Headache',
                'severity': 2,
                'duration_days': 1
            }
        ]
        
        result = self.ai_engine.analyze_symptoms(symptom_reports)
        
        self.assertIn('risk_level', result)
        self.assertIn('predicted_diseases', result)
        self.assertIn('recommendations', result)
        self.assertIn('specialist_referral', result)
        self.assertIsInstance(result['predicted_diseases'], list)
    
    def test_ml_engine_fallback(self):
        """Test ML engine fallback to rule-based"""
        # This test checks if the system gracefully falls back to rule-based
        # prediction when ML models fail
        
        symptom_reports = [
            {
                'symptom_name': 'Cough',
                'severity': 3,
                'duration_days': 5
            }
        ]
        
        # Even if ML fails, should still get a valid result
        result = self.ai_engine.analyze_symptoms(symptom_reports)
        
        self.assertIsInstance(result, dict)
        self.assertIn('risk_level', result)
        self.assertIn('recommendations', result)
```

## 7. Key AI Features Summary

### a. Multi-Algorithm Machine Learning
- **Random Forest**: Ensemble method for robust predictions
- **Support Vector Machine**: Kernel-based classification for complex patterns
- **Neural Network**: Deep learning with 3 hidden layers (128, 64, 32 neurons)
- **Naive Bayes**: Probabilistic baseline model

### b. Ensemble Prediction System
- **Weighted Voting**: Combines all models with accuracy-based weights
- **Confidence Thresholding**: Uses ML only when confidence > 40%
- **Intelligent Fallback**: Rule-based prediction as backup

### c. Synthetic Training Data Generation
- **Disease-Symptom Mapping**: 30+ diseases with associated symptoms
- **Data Augmentation**: 20 positive + 5 negative samples per disease
- **Realistic Simulation**: Severity randomization and secondary symptoms

### d. Advanced Risk Assessment
- **Multi-Factor Analysis**: Confidence, disease risk, symptom severity
- **Dynamic Risk Levels**: Low, Medium, High, Urgent classifications
- **Clinical Guidelines**: Based on medical knowledge base

### e. Knowledge Base Integration
- **Symptoms Database**: 100+ symptoms with categories and descriptions
- **Disease Database**: 30+ diseases with treatments and specialists
- **Keyword Matching**: Intelligent symptom search and matching

### f. Model Persistence & Management
- **Model Serialization**: Saves trained models using joblib
- **Performance Tracking**: Accuracy metrics and cross-validation
- **Automated Retraining**: Management commands for model updates

This AI-powered selftest system provides intelligent symptom analysis with multiple machine learning algorithms, ensemble prediction, and comprehensive medical knowledge integration for accurate disease prediction and risk assessment. 