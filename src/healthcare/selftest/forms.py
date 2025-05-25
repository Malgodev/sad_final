from django import forms
from django.core.exceptions import ValidationError
from .models import SelfTest, SymptomReport, Symptom
from .ai_engine import HealthAIEngine





class QuickTestForm(forms.Form):
    """Quick test form for rapid symptom analysis"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize AI engine to get symptoms
        ai_engine = HealthAIEngine()
        symptoms = ai_engine.symptoms_data.get('symptoms', [])
        
        # Create dynamic fields for symptoms
        for symptom in symptoms:
            field_name = f"symptom_{symptom['id']}"
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=symptom['name'],
                help_text=symptom['description'],
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input symptom-checkbox',
                    'data-symptom-name': symptom['name'],
                    'data-symptom-id': symptom['id']
                })
            )
            
            # Add severity field for each symptom
            severity_field_name = f"severity_{symptom['id']}"
            self.fields[severity_field_name] = forms.ChoiceField(
                choices=[(i, str(i)) for i in range(1, 5)],
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select severity-select',
                    'style': 'display: none;'
                }),
                help_text="Rate severity 1-4"
            )
    
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional symptoms or concerns...'
        }),
        help_text="Optional: Describe any other symptoms or health concerns"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if at least one symptom is selected
        selected_symptoms = []
        for field_name, value in cleaned_data.items():
            if field_name.startswith('symptom_') and value:
                symptom_id = field_name.replace('symptom_', '')
                severity_field = f"severity_{symptom_id}"
                severity = cleaned_data.get(severity_field)
                
                if not severity:
                    raise ValidationError(f"Please rate the severity for selected symptoms.")
                
                selected_symptoms.append({
                    'symptom_id': symptom_id,
                    'severity': int(severity)
                })
        
        if not selected_symptoms:
            raise ValidationError("Please select at least one symptom.")
        
        cleaned_data['selected_symptoms'] = selected_symptoms
        return cleaned_data


# Dynamic form factory for symptom selection
class SymptomSelectionFormSet:
    """Factory for creating dynamic symptom selection forms"""
    
    @staticmethod
    def create_symptom_forms(selected_symptoms):
        """Create forms for selected symptoms"""
        forms = []
        
        for symptom_data in selected_symptoms:
            # Get symptom object
            try:
                symptom = Symptom.objects.get(name=symptom_data['name'])
            except Symptom.DoesNotExist:
                continue
            
            # Create form for this symptom
            form = SymptomReportForm()
            form.symptom = symptom
            form.initial_severity = symptom_data.get('severity', 5)
            forms.append(form)
        
        return forms 