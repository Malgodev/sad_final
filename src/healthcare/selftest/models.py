from django.db import models
from django.contrib.auth.models import User
from patient.models import Patient


class Symptom(models.Model):
    """Symptom model for health tracking"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    severity_scale = models.CharField(max_length=50, default="1-4")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"


class SelfTest(models.Model):
    """Enhanced self-test model with AI analysis"""
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('urgent', 'Urgent - Seek Immediate Care'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='self_tests')
    symptoms = models.ManyToManyField(Symptom, through='SymptomReport')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, blank=True)
    ai_recommendation = models.TextField(blank=True)
    predicted_diseases = models.JSONField(default=list, blank=True)
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Self Test by {self.patient.user.get_full_name()} on {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Self Test"
        verbose_name_plural = "Self Tests"


class SymptomReport(models.Model):
    """Individual symptom report within a self-test"""
    SEVERITY_CHOICES = [
        (1, 'Mild'),
        (2, 'Moderate'),
        (3, 'Severe'),
        (4, 'Very Severe'),
    ]
    
    self_test = models.ForeignKey(SelfTest, on_delete=models.CASCADE, related_name='symptom_reports')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    duration_days = models.IntegerField(help_text="How many days have you had this symptom?")
    notes = models.TextField(blank=True, help_text="Additional details about this symptom")
    
    def __str__(self):
        return f"{self.symptom.name} - Severity {self.severity}"
    
    class Meta:
        unique_together = ['self_test', 'symptom']
        verbose_name = "Symptom Report"
        verbose_name_plural = "Symptom Reports"
