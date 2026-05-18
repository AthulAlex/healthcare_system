from django.contrib import admin
from .models import ResidentProfile, VitalSign, LabReport, AIHealthReport

@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'gender', 'blood_group', 'room_number', 'status', 'admission_date']
    search_fields = ['full_name', 'room_number']
    list_filter   = ['gender', 'status', 'blood_group']

@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display  = ['resident', 'blood_pressure', 'pulse_rate', 'oxygen_level', 'temperature', 'blood_sugar', 'is_abnormal', 'recorded_at']
    list_filter   = ['is_abnormal']
    search_fields = ['resident__full_name']

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display  = ['resident', 'test_name', 'result_value', 'unit', 'normal_range', 'is_critical', 'uploaded_at']
    list_filter   = ['is_critical']
    search_fields = ['resident__full_name', 'test_name']

@admin.register(AIHealthReport)
class AIHealthReportAdmin(admin.ModelAdmin):
    list_display  = ['resident', 'risk_level', 'risk_score', 'generated_at']
    list_filter   = ['risk_level']
    search_fields = ['resident__full_name']