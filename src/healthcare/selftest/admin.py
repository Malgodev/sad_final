from django.contrib import admin
from .models import SelfTest, Symptom, SymptomReport


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'severity_scale', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


class SymptomReportInline(admin.TabularInline):
    model = SymptomReport
    extra = 0
    readonly_fields = ['symptom', 'severity', 'duration_days']


@admin.register(SelfTest)
class SelfTestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'ai_recommendation']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SymptomReportInline]


@admin.register(SymptomReport)
class SymptomReportAdmin(admin.ModelAdmin):
    list_display = ['self_test', 'symptom', 'severity', 'duration_days']
    list_filter = ['severity', 'symptom', 'duration_days']
    search_fields = ['symptom__name', 'self_test__patient__user__first_name']
