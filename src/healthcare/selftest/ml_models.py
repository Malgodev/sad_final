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
    
    def _load_symptoms(self) -> Dict:
        """Load symptoms data from JSON file"""
        file_path = os.path.join(settings.BASE_DIR, 'selftest', 'data', 'symptoms.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Symptoms file not found: {file_path}")
            return {"symptoms": []}
    
    def _load_diseases(self) -> Dict:
        """Load diseases data from JSON file"""
        file_path = os.path.join(settings.BASE_DIR, 'selftest', 'data', 'diseases.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Diseases file not found: {file_path}")
            return {"diseases": []}
    
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
    
    def _prepare_input_features(self, symptom_reports: List[Dict]) -> Optional[np.ndarray]:
        """Prepare input features for ML models"""
        try:
            symptoms_list = [s['name'].lower() for s in self.symptoms_data.get('symptoms', [])]
            
            if not symptoms_list:
                return None
            
            # Create feature vector
            features = np.zeros(len(symptoms_list))
            
            for report in symptom_reports:
                symptom_name = report['symptom_name'].lower()
                severity = report['severity']
                
                if symptom_name in symptoms_list:
                    idx = symptoms_list.index(symptom_name)
                    features[idx] = severity
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))[0]
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Error preparing input features: {str(e)}")
            return None
    
    def _ensemble_predict(self, predictions: Dict, confidences: Dict) -> Tuple[str, float, str]:
        """Ensemble prediction using weighted voting"""
        disease_votes = {}
        total_weight = 0
        
        for model_name, disease in predictions.items():
            if disease == 'Unknown':
                continue
                
            confidence = confidences[model_name]
            model_accuracy = self.model_accuracies.get(model_name, {}).get('test_accuracy', 0.5)
            
            # Weight by model accuracy and confidence
            weight = model_accuracy * confidence
            
            if disease not in disease_votes:
                disease_votes[disease] = 0
            
            disease_votes[disease] += weight
            total_weight += weight
        
        if not disease_votes:
            return 'Unknown', 0.0, 'ensemble'
        
        # Get disease with highest weighted vote
        best_disease = max(disease_votes.keys(), key=lambda x: disease_votes[x])
        ensemble_confidence = disease_votes[best_disease] / total_weight if total_weight > 0 else 0.0
        
        return best_disease, ensemble_confidence, 'ensemble'
    
    def _get_disease_info(self, disease_name: str) -> Dict:
        """Get disease information from knowledge base"""
        for disease in self.diseases_data.get('diseases', []):
            if disease['name'] == disease_name:
                return disease
        
        # Return default info for unknown diseases
        return {
            'description': 'AI-predicted condition',
            'risk_level': 'medium',
            'treatment': 'Consult healthcare provider for proper diagnosis and treatment',
            'specialist': 'General Practitioner',
            'urgency': 'Schedule appointment with healthcare provider'
        }
    
    def _determine_ml_risk_level(self, confidence: float, disease_info: Dict, symptom_reports: List[Dict]) -> str:
        """Determine risk level based on ML prediction confidence and disease info"""
        disease_risk = disease_info.get('risk_level', 'medium')
        
        # High confidence and urgent disease
        if confidence > 0.8 and disease_risk == 'urgent':
            return 'urgent'
        
        # High confidence and high-risk disease
        if confidence > 0.7 and disease_risk == 'high':
            return 'high'
        
        # Moderate confidence with medium/high risk
        if confidence > 0.6 and disease_risk in ['medium', 'high']:
            return 'medium'
        
        # Check symptom severity
        avg_severity = np.mean([r['severity'] for r in symptom_reports])
        if avg_severity >= 3.5:  # High severity on 1-4 scale
            return 'high'
        elif avg_severity >= 2.5:
            return 'medium'
        
        return 'low'
    
    def _generate_ml_recommendations(self, disease_info: Dict, risk_level: str, confidence: float) -> str:
        """Generate ML-based recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == 'urgent':
            recommendations.append("🚨 URGENT: Seek immediate medical attention.")
        elif risk_level == 'high':
            recommendations.append("🔴 HIGH PRIORITY: Schedule appointment with healthcare provider within 24-48 hours.")
        elif risk_level == 'medium':
            recommendations.append("🟡 MODERATE: Consider scheduling appointment with healthcare provider within a week.")
        else:
            recommendations.append("🟢 LOW RISK: Monitor symptoms and consider self-care measures.")
        
        # AI confidence indication
        if confidence > 0.8:
            recommendations.append(f"🤖 AI Confidence: High ({confidence*100:.1f}%)")
        elif confidence > 0.6:
            recommendations.append(f"🤖 AI Confidence: Medium ({confidence*100:.1f}%)")
        else:
            recommendations.append(f"🤖 AI Confidence: Low ({confidence*100:.1f}%) - Consider comprehensive evaluation")
        
        # Disease-specific recommendations
        treatment = disease_info.get('treatment', '')
        if treatment:
            recommendations.append(f"💊 Suggested approach: {treatment}")
        
        # General advice
        recommendations.extend([
            "💧 Stay hydrated and get adequate rest",
            "🌡️ Monitor your symptoms and their progression",
            "📞 Contact healthcare provider if symptoms worsen"
        ])
        
        return "\n".join(recommendations)
    
    def _fallback_prediction(self, symptom_reports: List[Dict]) -> Dict:
        """Fallback to rule-based prediction when ML models are not available"""
        # Simple rule-based prediction as fallback
        return {
            'predicted_diseases': [],
            'risk_level': 'medium',
            'recommendations': 'ML models not available. Please consult a healthcare provider for proper diagnosis.',
            'specialist_referral': 'General Practitioner',
            'ml_confidence': 0.0,
            'model_used': 'fallback'
        }
    
    def _save_trained_models(self) -> None:
        """Save trained models to disk"""
        try:
            models_dir = os.path.join(settings.BASE_DIR, 'selftest', 'ml_models')
            os.makedirs(models_dir, exist_ok=True)
            
            # Save models
            for name, model in self.trained_models.items():
                model_path = os.path.join(models_dir, f'{name}_model.pkl')
                joblib.dump(model, model_path)
            
            # Save encoders and scaler
            joblib.dump(self.disease_encoder, os.path.join(models_dir, 'disease_encoder.pkl'))
            joblib.dump(self.scaler, os.path.join(models_dir, 'scaler.pkl'))
            
            # Save accuracies
            with open(os.path.join(models_dir, 'model_accuracies.json'), 'w') as f:
                json.dump(self.model_accuracies, f, indent=2)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def _load_trained_models(self) -> bool:
        """Load pre-trained models from disk"""
        try:
            models_dir = os.path.join(settings.BASE_DIR, 'selftest', 'ml_models')
            
            if not os.path.exists(models_dir):
                return False
            
            # Load encoders and scaler
            encoder_path = os.path.join(models_dir, 'disease_encoder.pkl')
            scaler_path = os.path.join(models_dir, 'scaler.pkl')
            
            if not (os.path.exists(encoder_path) and os.path.exists(scaler_path)):
                return False
            
            self.disease_encoder = joblib.load(encoder_path)
            self.scaler = joblib.load(scaler_path)
            
            # Load models
            for name in self.models.keys():
                model_path = os.path.join(models_dir, f'{name}_model.pkl')
                if os.path.exists(model_path):
                    self.trained_models[name] = joblib.load(model_path)
            
            # Load accuracies
            accuracies_path = os.path.join(models_dir, 'model_accuracies.json')
            if os.path.exists(accuracies_path):
                with open(accuracies_path, 'r') as f:
                    self.model_accuracies = json.load(f)
            
            self.is_trained = len(self.trained_models) > 0
            
            if self.is_trained:
                logger.info(f"Loaded {len(self.trained_models)} pre-trained models")
            
            return self.is_trained
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False
    
    def get_model_comparison(self) -> Dict:
        """Get comparison of all trained models"""
        if not self.model_accuracies:
            return {}
        
        comparison = {}
        for name, scores in self.model_accuracies.items():
            comparison[name] = {
                'test_accuracy': round(scores['test_accuracy'], 4),
                'cv_accuracy': round(scores['cv_accuracy'], 4),
                'cv_std': round(scores['cv_std'], 4),
                'status': 'trained' if name in self.trained_models else 'failed'
            }
        
        return comparison 