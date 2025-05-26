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

    def _generate_report(self, comparison):
        """Generate markdown report with model comparison"""
        report_content = self._create_report_content(comparison)
        
        # Save report
        report_path = os.path.join(settings.BASE_DIR, 'docs', 'ml_model_comparison.md')
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'Model comparison report saved to: {report_path}')
        )

    def _create_report_content(self, comparison):
        """Create markdown content for the model comparison report"""
        content = f"""# ML Model Comparison Report

Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This report compares the performance of different machine learning models trained for symptom-disease prediction in the Healthcare Self-Test system.

## Models Evaluated

The following models were trained and evaluated:

1. **Random Forest**: Ensemble method using multiple decision trees
2. **Support Vector Machine (SVM)**: Kernel-based classification with RBF kernel
3. **Neural Network (MLP)**: Multi-layer perceptron with 3 hidden layers (128, 64, 32 neurons)
4. **Naive Bayes**: Probabilistic classifier based on Bayes' theorem

## Training Data

- **Synthetic Data Generation**: Training data was generated from the existing symptom-disease knowledge base
- **Sample Size**: ~750 samples (30 diseases × 25 samples per disease)
- **Features**: {len([s for s in self._get_symptoms_count()])} symptom features with severity ratings (1-4 scale)
- **Labels**: {len([d for d in self._get_diseases_count()])} disease categories plus 'Other' class
- **Data Splitting**: 80% training, 20% testing with stratified sampling

## Model Performance

"""

        if not comparison:
            content += "❌ **No model performance data available**\n\n"
            content += "Models may not have been trained yet. Run `python manage.py train_ml_models` to train the models.\n"
            return content

        # Performance table
        content += "| Model | Test Accuracy | CV Accuracy | CV Std Dev | Status |\n"
        content += "|-------|---------------|-------------|------------|--------|\n"
        
        best_model = None
        best_accuracy = 0
        
        for model_name, metrics in comparison.items():
            test_acc = metrics['test_accuracy']
            cv_acc = metrics['cv_accuracy']
            cv_std = metrics['cv_std']
            status = metrics['status']
            
            if test_acc > best_accuracy:
                best_accuracy = test_acc
                best_model = model_name
            
            status_emoji = "✅" if status == "trained" else "❌"
            content += f"| {model_name.replace('_', ' ').title()} | {test_acc:.4f} | {cv_acc:.4f} | {cv_std:.4f} | {status_emoji} {status} |\n"

        content += "\n## Best Performing Model\n\n"
        if best_model:
            content += f"🏆 **{best_model.replace('_', ' ').title()}** achieved the highest test accuracy of **{best_accuracy:.4f}**\n\n"
        else:
            content += "❌ No successful model training results available\n\n"

        content += """## Model Details

### Random Forest
- **Algorithm**: Ensemble of decision trees with bootstrap aggregating
- **Parameters**: 100 estimators, max depth 10, balanced class weights
- **Advantages**: Handles non-linear relationships well, provides feature importance
- **Use Case**: Good baseline model with interpretable results

### Support Vector Machine (SVM)
- **Algorithm**: Kernel-based classification with RBF kernel
- **Parameters**: RBF kernel, probability estimates enabled, balanced class weights
- **Advantages**: Effective in high-dimensional spaces, memory efficient
- **Use Case**: Good for complex decision boundaries

### Neural Network (MLP)
- **Algorithm**: Multi-layer perceptron with backpropagation
- **Architecture**: Input layer → 128 → 64 → 32 → Output layer
- **Parameters**: Max 1000 iterations, early stopping, 10% validation split
- **Advantages**: Can learn complex non-linear patterns
- **Use Case**: Best for capturing intricate symptom-disease relationships

### Naive Bayes
- **Algorithm**: Gaussian Naive Bayes with independence assumption
- **Parameters**: Default scikit-learn configuration
- **Advantages**: Fast training and prediction, works well with small datasets
- **Use Case**: Baseline probabilistic model

## Ensemble Prediction

The system uses an **ensemble approach** that combines predictions from all trained models:

1. **Weighted Voting**: Each model's prediction is weighted by its accuracy and confidence
2. **Confidence Threshold**: ML prediction is used only if ensemble confidence > 40%
3. **Fallback**: Rule-based prediction when ML confidence is low

## Integration with Healthcare System

### API Compatibility
- All models maintain the same API interface as the original rule-based system
- No changes required to existing endpoints or frontend code
- Seamless fallback to rule-based prediction when needed

### Performance Monitoring
- Model predictions include confidence scores and model identification
- All predictions logged for continuous monitoring and improvement
- Fallback statistics tracked for system reliability

## Recommendations

"""

        if best_model:
            content += f"""### Production Deployment
1. **Primary Model**: Use {best_model.replace('_', ' ').title()} as the primary prediction model
2. **Ensemble**: Continue using ensemble approach for increased reliability
3. **Monitoring**: Implement prediction logging and performance monitoring
4. **Retraining**: Retrain models monthly with new data when available

### Model Improvements
1. **Data Collection**: Collect real patient data to improve training quality
2. **Feature Engineering**: Add temporal features and symptom interactions
3. **Model Tuning**: Perform hyperparameter optimization for better performance
4. **Validation**: Implement clinical validation with medical professionals

"""
        else:
            content += """### Next Steps
1. **Troubleshooting**: Investigate training failures and resolve technical issues
2. **Data Validation**: Verify symptom and disease data quality
3. **Environment**: Ensure all required ML libraries are properly installed
4. **Testing**: Run comprehensive tests on training pipeline

"""

        content += f"""## Technical Implementation

### File Structure
```
selftest/
├── ai_engine.py          # Main AI engine with ML integration
├── ml_models.py          # ML model implementations
├── data/
│   ├── symptoms.json     # Symptom knowledge base
│   └── diseases.json     # Disease knowledge base
└── ml_models/            # Trained model storage
    ├── random_forest_model.pkl
    ├── svm_model.pkl
    ├── neural_network_model.pkl
    ├── naive_bayes_model.pkl
    ├── disease_encoder.pkl
    └── scaler.pkl
```

### Usage Examples

```python
# Train models
python manage.py train_ml_models

# Force retrain
python manage.py train_ml_models --force

# Generate report only
python manage.py train_ml_models --report-only
```

---

*Report generated by Healthcare AI System v2.0*
*For technical support, contact the development team*
"""

        return content

    def _get_symptoms_count(self):
        """Get symptoms count for report"""
        try:
            ai_engine = HealthAIEngine()
            return ai_engine.symptoms_data.get('symptoms', [])
        except:
            return []

    def _get_diseases_count(self):
        """Get diseases count for report"""
        try:
            ai_engine = HealthAIEngine()
            return ai_engine.diseases_data.get('diseases', [])
        except:
            return [] 