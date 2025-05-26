# ML Model Comparison Report

Generated on: 2025-05-26 16:19:35

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
- **Features**: 35 symptom features with severity ratings (1-4 scale)
- **Labels**: 30 disease categories plus 'Other' class
- **Data Splitting**: 80% training, 20% testing with stratified sampling

## Model Performance

| Model | Test Accuracy | CV Accuracy | CV Std Dev | Status |
|-------|---------------|-------------|------------|--------|
| Random Forest | 0.6867 | 0.6813 | 0.0630 | ✅ trained |
| Svm | 0.6867 | 0.7133 | 0.0545 | ✅ trained |
| Neural Network | 0.7467 | 0.7360 | 0.0306 | ✅ trained |
| Naive Bayes | 0.2800 | 0.3013 | 0.0414 | ✅ trained |

## Best Performing Model

🏆 **Neural Network** achieved the highest test accuracy of **0.7467**

## Model Details

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

### Production Deployment
1. **Primary Model**: Use Neural Network as the primary prediction model
2. **Ensemble**: Continue using ensemble approach for increased reliability
3. **Monitoring**: Implement prediction logging and performance monitoring
4. **Retraining**: Retrain models monthly with new data when available

### Model Improvements
1. **Data Collection**: Collect real patient data to improve training quality
2. **Feature Engineering**: Add temporal features and symptom interactions
3. **Model Tuning**: Perform hyperparameter optimization for better performance
4. **Validation**: Implement clinical validation with medical professionals

## Technical Implementation

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
