from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, default='General Medicine')
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    experience_years = models.IntegerField(default=0)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_doctors')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status_indicator = "✓" if self.approval_status == 'approved' else "⏳" if self.approval_status == 'pending' else "✗"
        return f"{status_indicator} Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"

    @property
    def is_approved(self):
        return self.approval_status == 'approved'

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
