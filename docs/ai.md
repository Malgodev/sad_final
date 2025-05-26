# AI in Healthcare System

## 1. Application of Deep Learning in Healthcare

### 1.1 Deep Learning Architecture Overview

The Healthcare system leverages multiple deep learning approaches to enhance patient care and medical decision-making:

```mermaid
graph TB
    subgraph "Deep Learning Applications"
        SymptomAnalysis[🧠 Symptom Analysis<br/>- NLP for symptom extraction<br/>- Named Entity Recognition<br/>- Severity classification<br/>- Temporal pattern analysis]
        
        DiseasePredict[🔬 Disease Prediction<br/>- Multi-class classification<br/>- Ensemble methods<br/>- Probability estimation<br/>- Risk stratification]
        
        ImageAnalysis[📸 Medical Image Analysis<br/>- CNN for X-rays/MRI<br/>- Anomaly detection<br/>- Lesion segmentation<br/>- Diagnostic assistance]
        
        DrugInteraction[💊 Drug Interaction<br/>- Graph Neural Networks<br/>- Molecular analysis<br/>- Side effect prediction<br/>- Dosage optimization]
    end
    
    subgraph "AI Models"
        BERT[🤖 BERT/BioBERT<br/>- Medical text understanding<br/>- Context-aware processing<br/>- Domain-specific training<br/>- Multi-language support]
        
        CNN[🖼️ Convolutional Networks<br/>- Medical imaging<br/>- Feature extraction<br/>- Pattern recognition<br/>- Automated diagnosis]
        
        RNN[🔄 Recurrent Networks<br/>- Time series analysis<br/>- Patient monitoring<br/>- Trend prediction<br/>- Sequential data]
        
        Transformer[⚡ Transformers<br/>- Attention mechanisms<br/>- Long-range dependencies<br/>- Multi-modal fusion<br/>- Advanced reasoning]
    end
    
    subgraph "Data Sources"
        EHR[(📋 Electronic Health Records)]
        Symptoms[(🩺 Symptom Reports)]
        Images[(📷 Medical Images)]
        Labs[(🧪 Lab Results)]
        Wearables[(⌚ Wearable Data)]
    end
    
    %% Connections
    EHR --> SymptomAnalysis
    Symptoms --> SymptomAnalysis
    EHR --> DiseasePredict
    Images --> ImageAnalysis
    Labs --> DiseasePredict
    Wearables --> DiseasePredict
    
    SymptomAnalysis --> BERT
    DiseasePredict --> RNN
    ImageAnalysis --> CNN
    DrugInteraction --> Transformer
    
    %% Styling
    classDef dl fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class SymptomAnalysis,DiseasePredict,ImageAnalysis,DrugInteraction dl
    class BERT,CNN,RNN,Transformer model
    class EHR,Symptoms,Images,Labs,Wearables data
```

### 1.2 Symptom Analysis with NLP

#### 1.2.1 Natural Language Processing Pipeline

```python
# ai/nlp/symptom_analyzer.py
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Dict, Tuple

class SymptomAnalyzer(nn.Module):
    """Advanced NLP model for symptom analysis"""
    
    def __init__(self, model_name='dmis-lab/biobert-base-cased-v1.1'):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.bert = AutoModel.from_pretrained(model_name)
        
        # Classification heads
        self.symptom_classifier = nn.Linear(768, 256)
        self.severity_classifier = nn.Linear(768, 4)  # 1-4 scale
        self.urgency_classifier = nn.Linear(768, 3)   # low/medium/high
        self.entity_extractor = nn.Linear(768, 128)
        
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()
        
    def forward(self, input_ids, attention_mask):
        """Forward pass through the model"""
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        
        # Apply dropout
        pooled_output = self.dropout(pooled_output)
        
        # Classification outputs
        symptom_logits = self.symptom_classifier(pooled_output)
        severity_logits = self.severity_classifier(pooled_output)
        urgency_logits = self.urgency_classifier(pooled_output)
        
        return {
            'symptom_logits': symptom_logits,
            'severity_logits': severity_logits,
            'urgency_logits': urgency_logits,
            'embeddings': pooled_output
        }
    
    def extract_symptoms(self, text: str) -> Dict:
        """Extract symptoms from natural language text"""
        # Tokenize input
        inputs = self.tokenizer(
            text, 
            return_tensors='pt', 
            max_length=512, 
            truncation=True, 
            padding=True
        )
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.forward(inputs['input_ids'], inputs['attention_mask'])
        
        # Process outputs
        symptom_probs = torch.softmax(outputs['symptom_logits'], dim=-1)
        severity_probs = torch.softmax(outputs['severity_logits'], dim=-1)
        urgency_probs = torch.softmax(outputs['urgency_logits'], dim=-1)
        
        return {
            'symptoms': self._decode_symptoms(symptom_probs),
            'severity': self._decode_severity(severity_probs),
            'urgency': self._decode_urgency(urgency_probs),
            'confidence': float(torch.max(symptom_probs))
        }
    
    def _decode_symptoms(self, probs):
        """Decode symptom probabilities to symptom names"""
        # Implementation for symptom decoding
        pass
    
    def _decode_severity(self, probs):
        """Decode severity probabilities"""
        severity_map = {0: 'mild', 1: 'moderate', 2: 'severe', 3: 'critical'}
        return severity_map[torch.argmax(probs).item()]
    
    def _decode_urgency(self, probs):
        """Decode urgency probabilities"""
        urgency_map = {0: 'low', 1: 'medium', 2: 'high'}
        return urgency_map[torch.argmax(probs).item()]

# ai/nlp/medical_ner.py
import spacy
from spacy.training import Example
import json

class MedicalNER:
    """Named Entity Recognition for medical terms"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.medical_entities = self._load_medical_entities()
        
    def _load_medical_entities(self):
        """Load medical entity database"""
        return {
            'SYMPTOM': ['fever', 'headache', 'nausea', 'fatigue', 'cough'],
            'BODY_PART': ['head', 'chest', 'abdomen', 'back', 'leg'],
            'CONDITION': ['diabetes', 'hypertension', 'asthma', 'arthritis'],
            'MEDICATION': ['aspirin', 'ibuprofen', 'metformin', 'lisinopril'],
            'DURATION': ['days', 'weeks', 'months', 'hours', 'minutes']
        }
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract medical entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity_type = self._classify_medical_entity(ent.text.lower())
            if entity_type:
                entities.append({
                    'text': ent.text,
                    'label': entity_type,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': self._calculate_confidence(ent.text, entity_type)
                })
        
        return entities
    
    def _classify_medical_entity(self, text: str) -> str:
        """Classify text as medical entity type"""
        for entity_type, terms in self.medical_entities.items():
            if any(term in text for term in terms):
                return entity_type
        return None
    
    def _calculate_confidence(self, text: str, entity_type: str) -> float:
        """Calculate confidence score for entity classification"""
        # Simple confidence calculation based on exact match
        terms = self.medical_entities.get(entity_type, [])
        if text.lower() in terms:
            return 0.95
        elif any(term in text.lower() for term in terms):
            return 0.75
        else:
            return 0.5
```

### 1.3 Disease Prediction Models

#### 1.3.1 Multi-Modal Disease Prediction

```python
# ai/models/disease_predictor.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
import numpy as np

class MultiModalDiseasePredictor(nn.Module):
    """Multi-modal deep learning model for disease prediction"""
    
    def __init__(self, symptom_dim=100, lab_dim=50, demo_dim=10, num_diseases=200):
        super().__init__()
        
        # Symptom processing branch
        self.symptom_encoder = nn.Sequential(
            nn.Linear(symptom_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Lab results processing branch
        self.lab_encoder = nn.Sequential(
            nn.Linear(lab_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        
        # Demographics processing branch
        self.demo_encoder = nn.Sequential(
            nn.Linear(demo_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )
        
        # Attention mechanism for feature fusion
        self.attention = nn.MultiheadAttention(
            embed_dim=208,  # 128 + 64 + 16
            num_heads=8,
            dropout=0.1
        )
        
        # Final classification layers
        self.classifier = nn.Sequential(
            nn.Linear(208, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_diseases)
        )
        
        # Risk stratification head
        self.risk_classifier = nn.Linear(208, 4)  # low/medium/high/urgent
        
    def forward(self, symptoms, labs, demographics):
        """Forward pass through multi-modal network"""
        # Encode each modality
        symptom_features = self.symptom_encoder(symptoms)
        lab_features = self.lab_encoder(labs)
        demo_features = self.demo_encoder(demographics)
        
        # Concatenate features
        combined_features = torch.cat([symptom_features, lab_features, demo_features], dim=-1)
        
        # Apply attention mechanism
        combined_features = combined_features.unsqueeze(0)  # Add sequence dimension
        attended_features, _ = self.attention(
            combined_features, combined_features, combined_features
        )
        attended_features = attended_features.squeeze(0)
        
        # Final predictions
        disease_logits = self.classifier(attended_features)
        risk_logits = self.risk_classifier(attended_features)
        
        return {
            'disease_logits': disease_logits,
            'risk_logits': risk_logits,
            'features': attended_features
        }

class EnsembleDiseasePredictor:
    """Ensemble model combining multiple ML approaches"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'neural_network': MLPClassifier(hidden_layer_sizes=(256, 128, 64), random_state=42),
            'deep_learning': MultiModalDiseasePredictor()
        }
        self.weights = {'random_forest': 0.25, 'gradient_boost': 0.25, 'neural_network': 0.25, 'deep_learning': 0.25}
        
    def train(self, X_train, y_train):
        """Train all models in the ensemble"""
        for name, model in self.models.items():
            if name != 'deep_learning':
                model.fit(X_train, y_train)
            else:
                # Train deep learning model separately
                self._train_deep_model(model, X_train, y_train)
    
    def predict_proba(self, X):
        """Get ensemble predictions"""
        predictions = {}
        
        for name, model in self.models.items():
            if name != 'deep_learning':
                predictions[name] = model.predict_proba(X)
            else:
                predictions[name] = self._predict_deep_model(model, X)
        
        # Weighted ensemble
        ensemble_pred = np.zeros_like(predictions['random_forest'])
        for name, pred in predictions.items():
            ensemble_pred += self.weights[name] * pred
            
        return ensemble_pred
    
    def _train_deep_model(self, model, X, y):
        """Train deep learning model"""
        # Implementation for deep model training
        pass
    
    def _predict_deep_model(self, model, X):
        """Get predictions from deep learning model"""
        # Implementation for deep model prediction
        pass
```

### 1.4 Medical Image Analysis

#### 1.4.1 CNN for Medical Imaging

```python
# ai/vision/medical_imaging.py
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50, densenet121
import cv2
import numpy as np

class MedicalImageClassifier(nn.Module):
    """CNN for medical image classification"""
    
    def __init__(self, num_classes=10, backbone='resnet50'):
        super().__init__()
        
        if backbone == 'resnet50':
            self.backbone = resnet50(pretrained=True)
            self.backbone.fc = nn.Linear(2048, 512)
        elif backbone == 'densenet121':
            self.backbone = densenet121(pretrained=True)
            self.backbone.classifier = nn.Linear(1024, 512)
        
        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Conv2d(512, 256, 1),
            nn.ReLU(),
            nn.Conv2d(256, 1, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        """Forward pass through the network"""
        features = self.backbone(x)
        predictions = self.classifier(features)
        
        return {
            'predictions': predictions,
            'features': features
        }

class XRayAnalyzer:
    """Specialized analyzer for X-ray images"""
    
    def __init__(self, model_path=None):
        self.model = MedicalImageClassifier(num_classes=14)  # 14 common conditions
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.conditions = [
            'Normal', 'Pneumonia', 'COVID-19', 'Tuberculosis', 'Lung Cancer',
            'Pneumothorax', 'Pleural Effusion', 'Atelectasis', 'Cardiomegaly',
            'Consolidation', 'Edema', 'Emphysema', 'Fibrosis', 'Nodule'
        ]
    
    def analyze_xray(self, image_path: str) -> Dict:
        """Analyze X-ray image for abnormalities"""
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_tensor = self.transform(image).unsqueeze(0)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs['predictions'], dim=1)
        
        # Process results
        results = []
        for i, condition in enumerate(self.conditions):
            probability = float(probabilities[0][i])
            if probability > 0.1:  # Threshold for reporting
                results.append({
                    'condition': condition,
                    'probability': probability,
                    'confidence': self._calculate_confidence(probability)
                })
        
        # Sort by probability
        results.sort(key=lambda x: x['probability'], reverse=True)
        
        return {
            'findings': results,
            'normal_probability': float(probabilities[0][0]),
            'requires_attention': any(r['probability'] > 0.5 for r in results[1:])
        }
    
    def _calculate_confidence(self, probability: float) -> str:
        """Calculate confidence level based on probability"""
        if probability > 0.8:
            return 'high'
        elif probability > 0.6:
            return 'medium'
        else:
            return 'low'
```

## 2. Sentiment Analysis

### 2.1 Patient Sentiment Analysis Framework

```python
# ai/sentiment/patient_sentiment.py
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import Dict, List

class PatientSentimentAnalyzer:
    """Analyze patient sentiment from text communications"""
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment-latest')
        self.model = AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment-latest')
        
        # Custom medical sentiment categories
        self.medical_sentiments = {
            'anxiety': ['worried', 'anxious', 'scared', 'nervous', 'concerned'],
            'pain': ['hurts', 'painful', 'aching', 'sore', 'agony'],
            'satisfaction': ['better', 'improved', 'satisfied', 'pleased', 'grateful'],
            'frustration': ['frustrated', 'annoyed', 'upset', 'disappointed'],
            'urgency': ['urgent', 'emergency', 'immediate', 'critical', 'severe']
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of patient communication"""
        # Tokenize input
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Map to sentiment labels
        sentiment_labels = ['negative', 'neutral', 'positive']
        sentiment_scores = {
            label: float(prob) for label, prob in zip(sentiment_labels, probabilities[0])
        }
        
        # Analyze medical-specific sentiments
        medical_sentiments = self._analyze_medical_sentiment(text)
        
        # Calculate overall sentiment
        overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        confidence = sentiment_scores[overall_sentiment]
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': confidence,
            'sentiment_scores': sentiment_scores,
            'medical_sentiments': medical_sentiments,
            'emotional_indicators': self._extract_emotional_indicators(text),
            'urgency_level': self._assess_urgency(text, medical_sentiments)
        }
    
    def _analyze_medical_sentiment(self, text: str) -> Dict:
        """Analyze medical-specific sentiment categories"""
        text_lower = text.lower()
        medical_scores = {}
        
        for category, keywords in self.medical_sentiments.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            medical_scores[category] = min(score / len(keywords), 1.0)
        
        return medical_scores
    
    def _extract_emotional_indicators(self, text: str) -> List[str]:
        """Extract emotional indicators from text"""
        emotional_words = [
            'happy', 'sad', 'angry', 'worried', 'excited', 'depressed',
            'anxious', 'calm', 'stressed', 'relieved', 'hopeful', 'fearful'
        ]
        
        text_lower = text.lower()
        found_emotions = [word for word in emotional_words if word in text_lower]
        
        return found_emotions
    
    def _assess_urgency(self, text: str, medical_sentiments: Dict) -> str:
        """Assess urgency level based on sentiment analysis"""
        urgency_score = medical_sentiments.get('urgency', 0)
        pain_score = medical_sentiments.get('pain', 0)
        anxiety_score = medical_sentiments.get('anxiety', 0)
        
        combined_score = urgency_score * 0.5 + pain_score * 0.3 + anxiety_score * 0.2
        
        if combined_score > 0.7:
            return 'high'
        elif combined_score > 0.4:
            return 'medium'
        else:
            return 'low'

class FeedbackSentimentAnalyzer:
    """Analyze sentiment in patient feedback and reviews"""
    
    def __init__(self):
        self.aspect_categories = {
            'doctor_interaction': ['doctor', 'physician', 'professional', 'bedside manner'],
            'wait_time': ['wait', 'waiting', 'delay', 'appointment time', 'punctual'],
            'facility': ['clean', 'facility', 'environment', 'comfortable', 'equipment'],
            'staff': ['staff', 'nurse', 'receptionist', 'helpful', 'friendly'],
            'treatment': ['treatment', 'care', 'diagnosis', 'medication', 'therapy']
        }
    
    def analyze_feedback(self, feedback_text: str) -> Dict:
        """Analyze patient feedback for different aspects"""
        # Overall sentiment analysis
        overall_analysis = PatientSentimentAnalyzer().analyze_sentiment(feedback_text)
        
        # Aspect-based sentiment analysis
        aspect_sentiments = {}
        for aspect, keywords in self.aspect_categories.items():
            aspect_score = self._calculate_aspect_sentiment(feedback_text, keywords)
            aspect_sentiments[aspect] = aspect_score
        
        # Extract improvement suggestions
        suggestions = self._extract_suggestions(feedback_text)
        
        return {
            'overall_sentiment': overall_analysis,
            'aspect_sentiments': aspect_sentiments,
            'improvement_suggestions': suggestions,
            'satisfaction_score': self._calculate_satisfaction_score(aspect_sentiments),
            'key_issues': self._identify_key_issues(aspect_sentiments)
        }
    
    def _calculate_aspect_sentiment(self, text: str, keywords: List[str]) -> Dict:
        """Calculate sentiment for specific aspect"""
        # Find sentences containing aspect keywords
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                relevant_sentences.append(sentence.strip())
        
        if not relevant_sentences:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'mentions': 0}
        
        # Analyze sentiment of relevant sentences
        combined_text = ' '.join(relevant_sentences)
        sentiment_analysis = PatientSentimentAnalyzer().analyze_sentiment(combined_text)
        
        return {
            'sentiment': sentiment_analysis['overall_sentiment'],
            'confidence': sentiment_analysis['confidence'],
            'mentions': len(relevant_sentences),
            'text_snippets': relevant_sentences[:3]  # Top 3 mentions
        }
    
    def _calculate_satisfaction_score(self, aspect_sentiments: Dict) -> float:
        """Calculate overall satisfaction score from aspect sentiments"""
        weights = {
            'doctor_interaction': 0.3,
            'treatment': 0.25,
            'staff': 0.2,
            'wait_time': 0.15,
            'facility': 0.1
        }
        
        total_score = 0
        total_weight = 0
        
        for aspect, sentiment_data in aspect_sentiments.items():
            if sentiment_data['mentions'] > 0:
                weight = weights.get(aspect, 0.1)
                
                # Convert sentiment to score
                sentiment_score = {
                    'positive': 1.0,
                    'neutral': 0.5,
                    'negative': 0.0
                }.get(sentiment_data['sentiment'], 0.5)
                
                total_score += weight * sentiment_score * sentiment_data['confidence']
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
```

## 3. Applying Sentiment Analysis for Recommendation

### 3.1 Sentiment-Based Doctor Recommendation

```python
# ai/recommendation/sentiment_recommender.py
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class SentimentBasedRecommender:
    """Recommend doctors based on patient sentiment and preferences"""
    
    def __init__(self):
        self.doctor_sentiment_profiles = {}
        self.patient_sentiment_history = {}
        self.feedback_analyzer = FeedbackSentimentAnalyzer()
        
    def build_doctor_profiles(self, feedback_data: List[Dict]):
        """Build sentiment profiles for doctors based on patient feedback"""
        doctor_feedback = defaultdict(list)
        
        # Group feedback by doctor
        for feedback in feedback_data:
            doctor_id = feedback['doctor_id']
            doctor_feedback[doctor_id].append(feedback)
        
        # Analyze sentiment for each doctor
        for doctor_id, feedbacks in doctor_feedback.items():
            profile = self._create_doctor_sentiment_profile(feedbacks)
            self.doctor_sentiment_profiles[doctor_id] = profile
    
    def _create_doctor_sentiment_profile(self, feedbacks: List[Dict]) -> Dict:
        """Create sentiment profile for a doctor"""
        aspect_scores = defaultdict(list)
        overall_scores = []
        
        for feedback in feedbacks:
            analysis = self.feedback_analyzer.analyze_feedback(feedback['text'])
            
            # Collect aspect scores
            for aspect, sentiment_data in analysis['aspect_sentiments'].items():
                if sentiment_data['mentions'] > 0:
                    score = self._sentiment_to_score(sentiment_data['sentiment'])
                    aspect_scores[aspect].append(score * sentiment_data['confidence'])
            
            # Collect overall satisfaction
            overall_scores.append(analysis['satisfaction_score'])
        
        # Calculate average scores
        profile = {
            'overall_satisfaction': np.mean(overall_scores) if overall_scores else 0.5,
            'total_reviews': len(feedbacks),
            'aspect_scores': {}
        }
        
        for aspect, scores in aspect_scores.items():
            profile['aspect_scores'][aspect] = {
                'average': np.mean(scores),
                'std': np.std(scores),
                'count': len(scores)
            }
        
        return profile
    
    def recommend_doctors(self, patient_id: str, patient_preferences: Dict, 
                         available_doctors: List[Dict]) -> List[Dict]:
        """Recommend doctors based on patient sentiment preferences"""
        
        # Get patient sentiment history
        patient_profile = self._get_patient_sentiment_profile(patient_id)
        
        # Score each available doctor
        doctor_scores = []
        for doctor in available_doctors:
            doctor_id = doctor['id']
            
            if doctor_id in self.doctor_sentiment_profiles:
                score = self._calculate_compatibility_score(
                    patient_profile, 
                    self.doctor_sentiment_profiles[doctor_id],
                    patient_preferences
                )
                
                doctor_scores.append({
                    'doctor': doctor,
                    'compatibility_score': score,
                    'sentiment_match': self._get_sentiment_match_details(
                        patient_profile, self.doctor_sentiment_profiles[doctor_id]
                    )
                })
        
        # Sort by compatibility score
        doctor_scores.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return doctor_scores
    
    def _get_patient_sentiment_profile(self, patient_id: str) -> Dict:
        """Get or create patient sentiment profile"""
        if patient_id not in self.patient_sentiment_history:
            # Create default profile
            return {
                'preferred_aspects': ['doctor_interaction', 'treatment'],
                'sensitivity_to_wait_time': 0.5,
                'communication_preference': 'empathetic',
                'past_satisfaction_average': 0.5
            }
        
        return self.patient_sentiment_history[patient_id]
    
    def _calculate_compatibility_score(self, patient_profile: Dict, 
                                     doctor_profile: Dict, 
                                     preferences: Dict) -> float:
        """Calculate compatibility score between patient and doctor"""
        base_score = doctor_profile['overall_satisfaction']
        
        # Adjust based on patient preferences
        preference_bonus = 0
        
        for aspect in patient_profile['preferred_aspects']:
            if aspect in doctor_profile['aspect_scores']:
                aspect_score = doctor_profile['aspect_scores'][aspect]['average']
                preference_bonus += aspect_score * 0.2
        
        # Consider wait time sensitivity
        if 'wait_time' in doctor_profile['aspect_scores']:
            wait_score = doctor_profile['aspect_scores']['wait_time']['average']
            wait_sensitivity = patient_profile['sensitivity_to_wait_time']
            wait_adjustment = (wait_score - 0.5) * wait_sensitivity * 0.3
            preference_bonus += wait_adjustment
        
        # Consider review count (more reviews = more reliable)
        review_bonus = min(doctor_profile['total_reviews'] / 100, 0.1)
        
        final_score = base_score + preference_bonus + review_bonus
        return min(final_score, 1.0)
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment to numerical score"""
        return {'positive': 1.0, 'neutral': 0.5, 'negative': 0.0}.get(sentiment, 0.5)

class TreatmentRecommender:
    """Recommend treatments based on patient sentiment and outcomes"""
    
    def __init__(self):
        self.treatment_outcomes = {}
        self.patient_sentiment_tracker = {}
    
    def recommend_treatment_approach(self, patient_id: str, 
                                   condition: str, 
                                   patient_sentiment: Dict) -> Dict:
        """Recommend treatment approach based on patient sentiment"""
        
        # Analyze patient's emotional state
        emotional_state = self._analyze_emotional_state(patient_sentiment)
        
        # Get treatment options for condition
        treatment_options = self._get_treatment_options(condition)
        
        # Score treatments based on patient sentiment
        scored_treatments = []
        for treatment in treatment_options:
            score = self._score_treatment_for_patient(treatment, emotional_state)
            scored_treatments.append({
                'treatment': treatment,
                'suitability_score': score,
                'reasoning': self._explain_recommendation(treatment, emotional_state)
            })
        
        # Sort by suitability
        scored_treatments.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return {
            'recommended_treatments': scored_treatments,
            'patient_emotional_state': emotional_state,
            'communication_strategy': self._suggest_communication_strategy(emotional_state)
        }
    
    def _analyze_emotional_state(self, sentiment_data: Dict) -> Dict:
        """Analyze patient's emotional state from sentiment data"""
        return {
            'anxiety_level': sentiment_data['medical_sentiments'].get('anxiety', 0),
            'pain_level': sentiment_data['medical_sentiments'].get('pain', 0),
            'overall_mood': sentiment_data['overall_sentiment'],
            'urgency_perception': sentiment_data['urgency_level'],
            'emotional_indicators': sentiment_data['emotional_indicators']
        }
    
    def _score_treatment_for_patient(self, treatment: Dict, emotional_state: Dict) -> float:
        """Score treatment suitability based on patient's emotional state"""
        base_score = treatment['effectiveness_score']
        
        # Adjust for anxiety level
        if emotional_state['anxiety_level'] > 0.7:
            if treatment['invasiveness'] == 'low':
                base_score += 0.2
            elif treatment['invasiveness'] == 'high':
                base_score -= 0.3
        
        # Adjust for pain level
        if emotional_state['pain_level'] > 0.8:
            if treatment['pain_relief_speed'] == 'fast':
                base_score += 0.3
        
        # Adjust for overall mood
        if emotional_state['overall_mood'] == 'negative':
            if treatment['side_effects'] == 'minimal':
                base_score += 0.1
        
        return min(base_score, 1.0)
```

## 4. Deployment

### 4.1 Model Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LoadBalancer[🔄 Load Balancer<br/>Nginx/HAProxy]
        
        subgraph "API Gateway"
            Gateway[🌐 API Gateway<br/>- Authentication<br/>- Rate limiting<br/>- Request routing]
        end
        
        subgraph "AI Services"
            SymptomAPI[🧠 Symptom Analysis API<br/>- NLP processing<br/>- Entity extraction<br/>- Severity assessment]
            
            DiseaseAPI[🔬 Disease Prediction API<br/>- Multi-modal analysis<br/>- Risk stratification<br/>- Confidence scoring]
            
            SentimentAPI[😊 Sentiment Analysis API<br/>- Patient sentiment<br/>- Feedback analysis<br/>- Emotional state]
            
            RecommendAPI[💡 Recommendation API<br/>- Doctor matching<br/>- Treatment suggestions<br/>- Personalization]
        end
        
        subgraph "Model Serving"
            TorchServe[🔥 TorchServe<br/>- PyTorch models<br/>- GPU acceleration<br/>- Model versioning]
            
            TensorFlow[🧮 TensorFlow Serving<br/>- TF models<br/>- Batch processing<br/>- Auto-scaling]
            
            MLFlow[📊 MLFlow<br/>- Model registry<br/>- Experiment tracking<br/>- A/B testing]
        end
        
        subgraph "Data Pipeline"
            Kafka[📨 Apache Kafka<br/>- Real-time streaming<br/>- Event processing<br/>- Data ingestion]
            
            Airflow[🌊 Apache Airflow<br/>- Workflow orchestration<br/>- Model retraining<br/>- Data validation]
        end
        
        subgraph "Storage"
            ModelStore[(🗄️ Model Storage<br/>S3/MinIO)]
            FeatureStore[(📊 Feature Store<br/>Redis/Feast)]
            MetricsDB[(📈 Metrics DB<br/>InfluxDB)]
        end
        
        subgraph "Monitoring"
            Prometheus[📊 Prometheus<br/>- Metrics collection<br/>- Alerting<br/>- Performance monitoring]
            
            Grafana[📈 Grafana<br/>- Dashboards<br/>- Visualization<br/>- Alerts]
            
            ELK[🔍 ELK Stack<br/>- Log aggregation<br/>- Search<br/>- Analysis]
        end
    end
    
    %% Connections
    LoadBalancer --> Gateway
    Gateway --> SymptomAPI
    Gateway --> DiseaseAPI
    Gateway --> SentimentAPI
    Gateway --> RecommendAPI
    
    SymptomAPI --> TorchServe
    DiseaseAPI --> TensorFlow
    SentimentAPI --> TorchServe
    RecommendAPI --> MLFlow
    
    TorchServe --> ModelStore
    TensorFlow --> ModelStore
    MLFlow --> ModelStore
    
    SymptomAPI --> FeatureStore
    DiseaseAPI --> FeatureStore
    
    Kafka --> Airflow
    Airflow --> ModelStore
    
    SymptomAPI --> Prometheus
    DiseaseAPI --> Prometheus
    SentimentAPI --> Prometheus
    RecommendAPI --> Prometheus
    
    Prometheus --> Grafana
    Prometheus --> MetricsDB
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef serving fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storage fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef monitoring fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class Gateway,SymptomAPI,DiseaseAPI,SentimentAPI,RecommendAPI api
    class TorchServe,TensorFlow,MLFlow serving
    class Kafka,Airflow data
    class ModelStore,FeatureStore,MetricsDB storage
    class Prometheus,Grafana,ELK monitoring
```

### 4.2 Containerized Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  # AI API Services
  symptom-analyzer:
    build: ./ai/symptom-analyzer
    ports:
      - "8001:8000"
    environment:
      - MODEL_PATH=/models/symptom_analyzer.pth
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  disease-predictor:
    build: ./ai/disease-predictor
    ports:
      - "8002:8000"
    environment:
      - MODEL_PATH=/models/disease_predictor.pth
      - BATCH_SIZE=32
    volumes:
      - ./models:/models

  sentiment-analyzer:
    build: ./ai/sentiment-analyzer
    ports:
      - "8003:8000"
    environment:
      - TRANSFORMERS_CACHE=/cache
    volumes:
      - ./cache:/cache

  recommendation-engine:
    build: ./ai/recommendation-engine
    ports:
      - "8004:8000"
    depends_on:
      - redis
      - postgres

  # Model Serving
  torchserve:
    image: pytorch/torchserve:latest
    ports:
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./model-store:/home/model-server/model-store
      - ./config:/home/model-server/config
    command: torchserve --start --model-store /home/model-server/model-store --models all

  # Data Pipeline
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  airflow:
    image: apache/airflow:2.5.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./models:/opt/airflow/models
    depends_on:
      - postgres

  # Storage
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: healthcare_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  minio_data:
  grafana_data:
```

### 4.3 Kubernetes Deployment

```yaml
# k8s/ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: symptom-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: symptom-analyzer
  template:
    metadata:
      labels:
        app: symptom-analyzer
    spec:
      containers:
      - name: symptom-analyzer
        image: healthcare/symptom-analyzer:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        env:
        - name: MODEL_PATH
          value: "/models/symptom_analyzer.pth"
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: symptom-analyzer-service
spec:
  selector:
    app: symptom-analyzer
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: symptom-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: symptom-analyzer
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 4.4 CI/CD Pipeline

```yaml
# .github/workflows/ai-deployment.yml
name: AI Model Deployment

on:
  push:
    branches: [main]
    paths: ['ai/**', 'models/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r ai/requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest ai/tests/ --cov=ai/ --cov-report=xml
    
    - name: Model validation
      run: |
        python ai/scripts/validate_models.py

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker images
      run: |
        docker build -t healthcare/symptom-analyzer:${{ github.sha }} ai/symptom-analyzer/
        docker build -t healthcare/disease-predictor:${{ github.sha }} ai/disease-predictor/
        docker build -t healthcare/sentiment-analyzer:${{ github.sha }} ai/sentiment-analyzer/
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push healthcare/symptom-analyzer:${{ github.sha }}
        docker push healthcare/disease-predictor:${{ github.sha }}
        docker push healthcare/sentiment-analyzer:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/symptom-analyzer symptom-analyzer=healthcare/symptom-analyzer:${{ github.sha }}
        kubectl set image deployment/disease-predictor disease-predictor=healthcare/disease-predictor:${{ github.sha }}
        kubectl set image deployment/sentiment-analyzer sentiment-analyzer=healthcare/sentiment-analyzer:${{ github.sha }}
        kubectl rollout status deployment/symptom-analyzer
        kubectl rollout status deployment/disease-predictor
        kubectl rollout status deployment/sentiment-analyzer

  model-monitoring:
    needs: build-and-deploy
    runs-on: ubuntu-latest
    steps:
    - name: Setup model monitoring
      run: |
        python ai/scripts/setup_monitoring.py
        python ai/scripts/validate_deployment.py
```

### 4.5 Performance Optimization

```python
# ai/optimization/model_optimizer.py
import torch
import torch.quantization as quantization
from torch.jit import script
import onnx
import onnxruntime as ort

class ModelOptimizer:
    """Optimize AI models for production deployment"""
    
    def __init__(self):
        self.optimization_strategies = [
            'quantization',
            'pruning',
            'distillation',
            'onnx_conversion',
            'tensorrt_optimization'
        ]
    
    def optimize_model(self, model, strategy='quantization'):
        """Apply optimization strategy to model"""
        if strategy == 'quantization':
            return self._quantize_model(model)
        elif strategy == 'pruning':
            return self._prune_model(model)
        elif strategy == 'onnx_conversion':
            return self._convert_to_onnx(model)
        else:
            raise ValueError(f"Unknown optimization strategy: {strategy}")
    
    def _quantize_model(self, model):
        """Apply dynamic quantization to reduce model size"""
        model.eval()
        quantized_model = quantization.quantize_dynamic(
            model, 
            {torch.nn.Linear}, 
            dtype=torch.qint8
        )
        return quantized_model
    
    def _convert_to_onnx(self, model, input_shape=(1, 512)):
        """Convert PyTorch model to ONNX format"""
        model.eval()
        dummy_input = torch.randn(input_shape)
        
        torch.onnx.export(
            model,
            dummy_input,
            "model.onnx",
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        return "model.onnx"

# ai/monitoring/model_monitor.py
import numpy as np
from prometheus_client import Counter, Histogram, Gauge
import logging

class ModelMonitor:
    """Monitor AI model performance in production"""
    
    def __init__(self):
        # Prometheus metrics
        self.prediction_counter = Counter('ai_predictions_total', 'Total predictions', ['model', 'status'])
        self.prediction_latency = Histogram('ai_prediction_duration_seconds', 'Prediction latency', ['model'])
        self.model_accuracy = Gauge('ai_model_accuracy', 'Model accuracy', ['model'])
        self.data_drift_score = Gauge('ai_data_drift_score', 'Data drift score', ['model'])
        
        self.logger = logging.getLogger(__name__)
    
    def log_prediction(self, model_name, prediction_time, status='success'):
        """Log prediction metrics"""
        self.prediction_counter.labels(model=model_name, status=status).inc()
        self.prediction_latency.labels(model=model_name).observe(prediction_time)
    
    def update_accuracy(self, model_name, accuracy):
        """Update model accuracy metric"""
        self.model_accuracy.labels(model=model_name).set(accuracy)
    
    def detect_data_drift(self, reference_data, current_data, model_name):
        """Detect data drift using statistical tests"""
        from scipy import stats
        
        # Kolmogorov-Smirnov test for distribution comparison
        ks_statistic, p_value = stats.ks_2samp(reference_data, current_data)
        
        # Update drift score
        drift_score = ks_statistic
        self.data_drift_score.labels(model=model_name).set(drift_score)
        
        # Alert if significant drift detected
        if p_value < 0.05:
            self.logger.warning(f"Data drift detected for {model_name}: KS={ks_statistic:.3f}, p={p_value:.3f}")
            return True
        
        return False
```

---

*This AI document provides a comprehensive overview of deep learning applications in the Healthcare system, including advanced NLP for symptom analysis, sentiment analysis for patient feedback, recommendation systems, and production deployment strategies with monitoring and optimization.* 