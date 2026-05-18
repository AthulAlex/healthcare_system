from django.db import models
from accounts.models import CustomUser

class ResidentProfile(models.Model):
    STATUS_CHOICES = (
        ('active',     'Active'),
        ('inactive',   'Inactive'),
        ('discharged', 'Discharged'),
    )
    user               = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name          = models.CharField(max_length=100)
    date_of_birth      = models.DateField()
    gender             = models.CharField(max_length=10)
    blood_group        = models.CharField(max_length=5)
    address            = models.TextField()
    emergency_contact  = models.CharField(max_length=15)
    admission_date     = models.DateField(auto_now_add=True)
    medical_history    = models.TextField(blank=True)
    assigned_caregiver = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name='residents'
    )
    assigned_doctor    = models.ForeignKey(   # ← add this
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doctor_residents'
    )
    room_number = models.CharField(max_length=20, blank=True, default='')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.full_name


class VitalSign(models.Model):
    resident       = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='vitals')
    recorded_at    = models.DateTimeField(auto_now_add=True)
    blood_pressure = models.CharField(max_length=20)
    pulse_rate     = models.IntegerField()
    oxygen_level   = models.FloatField()
    temperature    = models.FloatField()
    blood_sugar    = models.FloatField()
    notes          = models.TextField(blank=True)
    is_abnormal    = models.BooleanField(default=False)

    def __str__(self):
        return f"Vitals of {self.resident.full_name} at {self.recorded_at}"


class LabReport(models.Model):
    resident     = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='lab_reports')
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    test_name    = models.CharField(max_length=100)
    result_value = models.FloatField()
    normal_range = models.CharField(max_length=50)
    unit         = models.CharField(max_length=20)
    is_critical  = models.BooleanField(default=False)
    pdf_report   = models.FileField(upload_to='lab_reports/', blank=True, null=True)

    def __str__(self):
        return f"{self.test_name} - {self.resident.full_name}"


class AIHealthReport(models.Model):
    resident     = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name='ai_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    risk_score   = models.IntegerField(default=0)
    risk_level   = models.CharField(max_length=20, default='Low')
    summary      = models.TextField()
    factors      = models.TextField(blank=True)

    def __str__(self):
        return f"AI Report for {self.resident.full_name} on {self.generated_at.strftime('%d %b %Y')}"