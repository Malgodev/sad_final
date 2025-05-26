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
    
    def _rule_based_prediction(self, symptom_reports: List[Dict]) -> Dict:
        """Rule-based prediction as fallback when ML models fail"""
        # Extract symptom names and severities
        reported_symptoms = {report['symptom_name'].lower(): report['severity'] for report in symptom_reports}
        
        # Calculate disease confidence scores
        disease_scores = []
        for disease in self.diseases_data.get('diseases', []):
            confidence = self._calculate_disease_confidence(disease, reported_symptoms)
            if confidence > 0:
                disease_scores.append({
                    'name': disease['name'],
                    'description': disease['description'],
                    'confidence': confidence,
                    'risk_level': disease['risk_level'],
                    'treatment': disease['treatment'],
                    'specialist': disease['specialist'],
                    'urgency': disease['urgency']
                })
        
        # Sort by confidence score
        disease_scores.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Determine overall risk level
        overall_risk = self._determine_risk_level(disease_scores, symptom_reports)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(disease_scores, overall_risk)
        
        # Get specialist referral
        specialist_referral = self._get_specialist_referral(disease_scores)
        
        return {
            'predicted_diseases': disease_scores[:5],  # Top 5 predictions
            'risk_level': overall_risk,
            'recommendations': recommendations,
            'specialist_referral': specialist_referral,
            'ml_confidence': 0.0,
            'model_used': 'rule_based'
        }
    
    def _calculate_disease_confidence(self, disease: Dict, reported_symptoms: Dict) -> float:
        """Calculate confidence score for a disease based on reported symptoms"""
        disease_symptoms = [s.lower() for s in disease.get('symptoms', [])]
        
        if not disease_symptoms:
            return 0.0
        
        # Count matching symptoms
        matching_symptoms = 0
        severity_bonus = 0
        
        for symptom in disease_symptoms:
            if symptom in reported_symptoms:
                matching_symptoms += 1
                # Add bonus for higher severity (adjusted for 1-4 scale)
                severity = reported_symptoms[symptom]
                severity_bonus += min(severity / 4.0, 1.0) * 0.1
        
        # Base confidence is percentage of matching symptoms
        base_confidence = (matching_symptoms / len(disease_symptoms)) * 100
        
        # Add severity bonus (max 10% additional)
        confidence = min(base_confidence + (severity_bonus * 100), 100.0)
        
        return round(confidence, 1)
    
    def _determine_risk_level(self, disease_scores: List[Dict], symptom_reports: List[Dict]) -> str:
        """Determine overall risk level based on predicted diseases and symptom severity"""
        if not disease_scores:
            return 'low'
        
        # Check for urgent conditions
        for disease in disease_scores[:3]:  # Top 3 predictions
            if disease['risk_level'] == 'urgent' and disease['confidence'] > 30:
                return 'urgent'
        
        # Check for high-risk conditions
        for disease in disease_scores[:3]:
            if disease['risk_level'] == 'high' and disease['confidence'] > 40:
                return 'high'
        
        # Check symptom severity (adjusted for 1-4 scale)
        high_severity_count = sum(1 for report in symptom_reports if report['severity'] >= 4)
        very_severe_count = sum(1 for report in symptom_reports if report['severity'] >= 3)
        if high_severity_count >= 1:
            return 'high'
        if very_severe_count >= 2:
            return 'high'
        
        # Check for medium-risk conditions
        for disease in disease_scores[:3]:
            if disease['risk_level'] in ['medium', 'high'] and disease['confidence'] > 50:
                return 'medium'
        
        return 'low'
    
    def _generate_recommendations(self, disease_scores: List[Dict], risk_level: str) -> str:
        """Generate health recommendations based on analysis"""
        if not disease_scores:
            return "No specific conditions identified. Maintain healthy lifestyle and consult healthcare provider if symptoms persist."
        
        top_disease = disease_scores[0]
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == 'urgent':
            recommendations.append("⚠️ URGENT: Seek immediate medical attention.")
        elif risk_level == 'high':
            recommendations.append("🔴 HIGH PRIORITY: Schedule appointment with healthcare provider within 24-48 hours.")
        elif risk_level == 'medium':
            recommendations.append("🟡 MODERATE: Consider scheduling appointment with healthcare provider within a week.")
        else:
            recommendations.append("🟢 LOW RISK: Monitor symptoms and consider self-care measures.")
        
        # Disease-specific recommendations
        if top_disease['confidence'] > 60:
            recommendations.append(f"Most likely condition: {top_disease['name']}")
            recommendations.append(f"Recommended treatment: {top_disease['treatment']}")
        
        # General advice
        recommendations.extend([
            "💧 Stay hydrated and get adequate rest",
            "🌡️ Monitor your symptoms and their progression",
            "📞 Contact healthcare provider if symptoms worsen"
        ])
        
        return "\n".join(recommendations)
    
    def _get_specialist_referral(self, disease_scores: List[Dict]) -> str:
        """Get specialist referral recommendation"""
        if not disease_scores:
            return "General Practitioner"
        
        top_disease = disease_scores[0]
        if top_disease['confidence'] > 50:
            return top_disease['specialist']
        
        return "General Practitioner"
    
    def get_symptom_by_name(self, name: str) -> Dict:
        """Get symptom details by name"""
        for symptom in self.symptoms_data.get('symptoms', []):
            if symptom['name'].lower() == name.lower():
                return symptom
        return None
    
    def _train_ml_models(self) -> Dict[str, float]:
        """Train ML models and return accuracies"""
        try:
            print("Training AI models... This may take a few minutes.")
            accuracies = self.ml_engine.train_models()
            print("AI model training completed!")
            return accuracies
        except Exception as e:
            print(f"ML model training failed: {str(e)}")
            return {}
    
    def get_model_comparison(self) -> Dict:
        """Get performance comparison of all ML models"""
        return self.ml_engine.get_model_comparison()
    
    def force_retrain_models(self) -> Dict[str, float]:
        """Force retrain all ML models"""
        return self.ml_engine.train_models()