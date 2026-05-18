from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('caregiver',   'Caregiver'),
        ('resident',    'Resident'),
        ('stockkeeper', 'Stock Keeper'),
        ('doctor',      'Doctor'),
    )

    SPECIALIZATION_CHOICES = (
        ('general',        'General Medicine'),
        ('cardiology',     'Cardiology'),
        ('neurology',      'Neurology'),
        ('orthopedics',    'Orthopedics'),
        ('endocrinology',  'Endocrinology'),
        ('nephrology',     'Nephrology'),
        ('pulmonology',    'Pulmonology'),
        ('gastroenterology','Gastroenterology'),
        ('ophthalmology',  'Ophthalmology'),
        ('dermatology',    'Dermatology'),
        ('psychiatry',     'Psychiatry'),
        ('oncology',       'Oncology'),
        ('other',          'Other'),
    )

    DEPARTMENT_CHOICES = (
        ('general_ward',   'General Ward'),
        ('icu',            'ICU'),
        ('cardiology_dept','Cardiology Department'),
        ('neurology_dept', 'Neurology Department'),
        ('orthopedics_dept','Orthopedics Department'),
        ('outpatient',     'Outpatient Department'),
        ('emergency',      'Emergency'),
        ('other',          'Other'),
    )

    role           = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    phone          = models.CharField(max_length=15, blank=True, default='')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES,
                                      blank=True, default='general')
    department     = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES,
                                      blank=True, default='general_ward')
    qualification  = models.CharField(max_length=100, blank=True, default='')
    experience_years = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_full_title(self):
        if self.role == 'doctor':
            return f"Dr. {self.username}"
        return self.username