import json
import os
from typing import List, Dict, Tuple
from django.conf import settings
from doctor.models import Doctor
from django.db.models import Q


class AppointmentChatbot:
    """AI Chatbot for appointment recommendations based on diseases and criteria"""
    
    def __init__(self):
        self.disease_specialization_map = self._load_disease_specialization_mapping()
        self.specialization_keywords = self._load_specialization_keywords()
    
    def _load_disease_specialization_mapping(self) -> Dict:
        """Load disease to specialization mapping"""
        return {
            # Cardiovascular diseases
            "heart disease": ["Cardiology", "Internal Medicine"],
            "chest pain": ["Cardiology", "Emergency Medicine", "Internal Medicine"],
            "high blood pressure": ["Cardiology", "Internal Medicine", "Family Medicine"],
            "heart attack": ["Cardiology", "Emergency Medicine"],
            "arrhythmia": ["Cardiology"],
            "heart failure": ["Cardiology", "Internal Medicine"],
            
            # Respiratory diseases
            "asthma": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "pneumonia": ["Pulmonology", "Internal Medicine", "Emergency Medicine"],
            "bronchitis": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "cough": ["Pulmonology", "Internal Medicine", "Family Medicine"],
            "shortness of breath": ["Pulmonology", "Cardiology", "Internal Medicine"],
            "lung disease": ["Pulmonology"],
            
            # Gastrointestinal diseases
            "stomach pain": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "nausea": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "diarrhea": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "constipation": ["Gastroenterology", "Internal Medicine", "Family Medicine"],
            "acid reflux": ["Gastroenterology", "Internal Medicine"],
            "ulcer": ["Gastroenterology", "Internal Medicine"],
            
            # Neurological diseases
            "headache": ["Neurology", "Internal Medicine", "Family Medicine"],
            "migraine": ["Neurology", "Internal Medicine"],
            "seizure": ["Neurology", "Emergency Medicine"],
            "stroke": ["Neurology", "Emergency Medicine"],
            "memory loss": ["Neurology", "Geriatrics"],
            "dizziness": ["Neurology", "Internal Medicine", "ENT"],
            
            # Orthopedic conditions
            "back pain": ["Orthopedics", "Physical Medicine", "Family Medicine"],
            "joint pain": ["Orthopedics", "Rheumatology", "Internal Medicine"],
            "fracture": ["Orthopedics", "Emergency Medicine"],
            "arthritis": ["Rheumatology", "Orthopedics", "Internal Medicine"],
            "muscle pain": ["Orthopedics", "Physical Medicine", "Family Medicine"],
            
            # Dermatological conditions
            "skin rash": ["Dermatology", "Family Medicine", "Internal Medicine"],
            "acne": ["Dermatology", "Family Medicine"],
            "eczema": ["Dermatology", "Allergy and Immunology"],
            "psoriasis": ["Dermatology"],
            "skin cancer": ["Dermatology", "Oncology"],
            
            # Endocrine disorders
            "diabetes": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            "thyroid": ["Endocrinology", "Internal Medicine"],
            "weight loss": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            "weight gain": ["Endocrinology", "Internal Medicine", "Family Medicine"],
            
            # Mental health
            "depression": ["Psychiatry", "Psychology", "Family Medicine"],
            "anxiety": ["Psychiatry", "Psychology", "Family Medicine"],
            "stress": ["Psychiatry", "Psychology", "Family Medicine"],
            "insomnia": ["Psychiatry", "Sleep Medicine", "Internal Medicine"],
            
            # Women's health
            "pregnancy": ["Obstetrics and Gynecology", "Family Medicine"],
            "menstrual": ["Obstetrics and Gynecology", "Family Medicine"],
            "pelvic pain": ["Obstetrics and Gynecology", "Internal Medicine"],
            
            # General symptoms
            "fever": ["Internal Medicine", "Family Medicine", "Emergency Medicine"],
            "fatigue": ["Internal Medicine", "Family Medicine"],
            "weight loss": ["Internal Medicine", "Oncology", "Endocrinology"],
            "pain": ["Internal Medicine", "Family Medicine", "Pain Management"],
            "infection": ["Internal Medicine", "Family Medicine", "Infectious Disease"],
            
            # Emergency conditions
            "emergency": ["Emergency Medicine"],
            "trauma": ["Emergency Medicine", "Surgery"],
            "accident": ["Emergency Medicine", "Surgery", "Orthopedics"],
        }
    
    def _load_specialization_keywords(self) -> Dict:
        """Load keywords for each specialization"""
        return {
            "Cardiology": ["heart", "cardiac", "cardiovascular", "chest pain", "blood pressure", "arrhythmia"],
            "Pulmonology": ["lung", "respiratory", "breathing", "cough", "asthma", "pneumonia"],
            "Gastroenterology": ["stomach", "digestive", "intestinal", "bowel", "liver", "gallbladder"],
            "Neurology": ["brain", "neurological", "headache", "seizure", "stroke", "memory"],
            "Orthopedics": ["bone", "joint", "muscle", "fracture", "spine", "back pain"],
            "Dermatology": ["skin", "rash", "acne", "eczema", "mole", "dermatitis"],
            "Endocrinology": ["diabetes", "thyroid", "hormone", "metabolism", "weight"],
            "Psychiatry": ["mental", "depression", "anxiety", "stress", "mood", "psychiatric"],
            "Obstetrics and Gynecology": ["women", "pregnancy", "gynecological", "menstrual", "reproductive"],
            "Emergency Medicine": ["emergency", "urgent", "trauma", "accident", "critical"],
            "Internal Medicine": ["general", "internal", "primary care", "chronic", "medical"],
            "Family Medicine": ["family", "primary", "general practice", "preventive"],
            "Pediatrics": ["children", "pediatric", "infant", "child", "adolescent"],
            "Surgery": ["surgical", "operation", "procedure", "tumor", "mass"],
            "Oncology": ["cancer", "tumor", "oncology", "chemotherapy", "radiation"],
            "Rheumatology": ["arthritis", "autoimmune", "joint inflammation", "lupus"],
            "Urology": ["kidney", "bladder", "urinary", "prostate", "urological"],
            "ENT": ["ear", "nose", "throat", "sinus", "hearing", "voice"],
            "Ophthalmology": ["eye", "vision", "sight", "retina", "glaucoma"],
            "Anesthesiology": ["anesthesia", "pain management", "surgical anesthesia"],
        }
    
    def analyze_user_input(self, user_message: str, criteria: Dict = None) -> Dict:
        """
        Analyze user input and recommend doctors
        
        Args:
            user_message: User's description of disease/symptoms
            criteria: Additional criteria like location, experience, etc.
        
        Returns:
            Dict with recommended doctors and analysis
        """
        user_message_lower = user_message.lower()
        
        # Find matching specializations
        recommended_specializations = self._find_specializations(user_message_lower)
        
        # Get available doctors
        recommended_doctors = self._get_recommended_doctors(
            recommended_specializations, 
            criteria or {}
        )
        
        # Generate response message
        response_message = self._generate_response_message(
            user_message, 
            recommended_specializations, 
            recommended_doctors
        )
        
        return {
            'message': response_message,
            'recommended_doctors': recommended_doctors,
            'specializations': recommended_specializations,
            'confidence': self._calculate_confidence(user_message_lower, recommended_specializations)
        }
    
    def _find_specializations(self, user_input: str) -> List[Dict]:
        """Find matching specializations based on user input"""
        specialization_scores = {}
        
        # Check disease mapping
        for disease, specializations in self.disease_specialization_map.items():
            if disease in user_input:
                for spec in specializations:
                    specialization_scores[spec] = specialization_scores.get(spec, 0) + 3
        
        # Check keyword mapping
        for specialization, keywords in self.specialization_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    specialization_scores[specialization] = specialization_scores.get(specialization, 0) + 1
        
        # Sort by score and return top specializations
        sorted_specs = sorted(specialization_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'name': spec,
                'score': score,
                'relevance': min(score * 20, 100)  # Convert to percentage
            }
            for spec, score in sorted_specs[:5]
        ]
    
    def _get_recommended_doctors(self, specializations: List[Dict], criteria: Dict) -> List[Dict]:
        """Get recommended doctors based on specializations and criteria"""
        if not specializations:
            # If no specific specialization found, recommend general practitioners
            specializations = [{'name': 'Internal Medicine'}, {'name': 'Family Medicine'}]
        
        # Build query
        spec_names = [spec['name'] for spec in specializations]
        query = Q(specialization__in=spec_names) & Q(approval_status='approved')
        
        # Apply additional criteria
        if criteria.get('min_experience'):
            query &= Q(experience_years__gte=criteria['min_experience'])
        
        # Get doctors
        doctors = Doctor.objects.filter(query).select_related('user').order_by('-experience_years')[:10]
        
        recommended_doctors = []
        for doctor in doctors:
            # Calculate relevance score
            relevance = 50  # Base score
            for spec in specializations:
                if spec['name'] == doctor.specialization:
                    relevance += spec.get('relevance', 50)
                    break
            
            # Experience bonus
            if doctor.experience_years > 10:
                relevance += 20
            elif doctor.experience_years > 5:
                relevance += 10
            
            relevance = min(relevance, 100)
            
            recommended_doctors.append({
                'id': doctor.id,
                'name': doctor.user.get_full_name(),
                'specialization': doctor.specialization,
                'experience_years': doctor.experience_years,
                'phone': doctor.phone,
                'license_number': doctor.license_number,
                'relevance_score': relevance
            })
        
        # Sort by relevance score
        recommended_doctors.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommended_doctors
    
    def _generate_response_message(self, user_input: str, specializations: List[Dict], doctors: List[Dict]) -> str:
        """Generate chatbot response message"""
        if not doctors:
            return """I understand you're looking for medical assistance, but I couldn't find specific doctors for your condition. 
            I recommend consulting with a General Medicine or Family Medicine doctor who can evaluate your symptoms and refer you to the appropriate specialist if needed."""
        
        response_parts = []
        
        # Greeting and understanding
        response_parts.append(f"I understand you're experiencing: '{user_input}'")
        
        # Specialization recommendation
        if specializations:
            top_spec = specializations[0]
            response_parts.append(f"Based on your description, I recommend consulting with a {top_spec['name']} specialist.")
        
        # Doctor recommendations with direct links
        if len(doctors) == 1:
            doctor = doctors[0]
            response_parts.append(f"I found an excellent doctor for you:")
            response_parts.append(f"🔗 Dr. {doctor['name']} ({doctor['specialization']}) - {doctor['experience_years']} years experience")
            response_parts.append(f"📋 View full profile: /doctor/profile/{doctor['id']}/")
            response_parts.append(f"📅 Book appointment: /patient/appointments/calendar/?doctor={doctor['id']}")
        else:
            response_parts.append(f"I found {len(doctors)} qualified doctors who can help you:")
            for i, doctor in enumerate(doctors[:3], 1):
                response_parts.append(f"\n{i}. 🔗 Dr. {doctor['name']} - {doctor['specialization']} ({doctor['experience_years']} years)")
                response_parts.append(f"   📋 Profile: /doctor/profile/{doctor['id']}/")
                response_parts.append(f"   📅 Book: /patient/appointments/calendar/?doctor={doctor['id']}")
        
        # Next steps
        response_parts.append("\n💡 Click the links above to view doctor profiles and book appointments directly!")
        response_parts.append("You can also use the 'Profile' and 'Book Now' buttons in the doctor cards below.")
        
        return "\n".join(response_parts)
    
    def _calculate_confidence(self, user_input: str, specializations: List[Dict]) -> int:
        """Calculate confidence score for the recommendation"""
        if not specializations:
            return 30
        
        # Base confidence on number of matching keywords/diseases
        confidence = min(specializations[0].get('relevance', 50), 90)
        
        # Boost confidence for specific disease mentions
        for disease in self.disease_specialization_map.keys():
            if disease in user_input:
                confidence = min(confidence + 20, 95)
                break
        
        return max(confidence, 40)  # Minimum 40% confidence
    
    def get_quick_suggestions(self) -> List[str]:
        """Get quick suggestion prompts for users"""
        return [
            "I have chest pain and shortness of breath",
            "I'm experiencing severe headaches",
            "I have stomach pain and nausea",
            "I need help with diabetes management",
            "I have back pain that won't go away",
            "I'm feeling anxious and depressed",
            "I have a skin rash that's spreading",
            "I need a general health checkup",
            "I'm pregnant and need prenatal care",
            "I have joint pain and stiffness"
        ]
    
    def get_specialization_info(self, specialization: str) -> Dict:
        """Get information about a specific specialization"""
        info_map = {
            "Cardiology": {
                "description": "Heart and cardiovascular system specialists",
                "treats": ["Heart disease", "High blood pressure", "Chest pain", "Arrhythmia"],
                "when_to_see": "Chest pain, heart palpitations, high blood pressure"
            },
            "Pulmonology": {
                "description": "Lung and respiratory system specialists",
                "treats": ["Asthma", "Pneumonia", "Bronchitis", "Lung disease"],
                "when_to_see": "Persistent cough, breathing difficulties, chest congestion"
            },
            "Gastroenterology": {
                "description": "Digestive system specialists",
                "treats": ["Stomach pain", "Acid reflux", "Ulcers", "Liver disease"],
                "when_to_see": "Stomach pain, digestive issues, bowel problems"
            },
            "Neurology": {
                "description": "Brain and nervous system specialists",
                "treats": ["Headaches", "Seizures", "Stroke", "Memory problems"],
                "when_to_see": "Severe headaches, neurological symptoms, memory issues"
            },
            "Internal Medicine": {
                "description": "General adult medicine specialists",
                "treats": ["General health", "Chronic diseases", "Preventive care"],
                "when_to_see": "General health concerns, routine checkups, chronic conditions"
            }
        }
        
        return info_map.get(specialization, {
            "description": f"{specialization} specialist",
            "treats": ["Various conditions in this specialty"],
            "when_to_see": "Conditions related to this medical specialty"
        }) 