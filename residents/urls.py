from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',   views.resident_dashboard,  name='resident_dashboard'),
    path('vitals/',      views.vital_history,        name='vital_history'),
    path('labs/',        views.lab_reports,           name='lab_reports'),
    path('export-pdf/',  views.export_pdf,            name='export_pdf'),
    path('ai-report/',   views.ai_health_report,      name='ai_health_report'),
]