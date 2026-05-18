from django.contrib import admin
from .models import Medicine, Prescription

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display  = ['name', 'batch_number', 'supplier', 'quantity', 'minimum_stock', 'expiry_date']
    search_fields = ['name', 'batch_number', 'supplier']
    list_filter   = ['supplier']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ['resident', 'medicine', 'dosage', 'frequency', 'prescribed_by', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['resident__full_name', 'medicine__name']