from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                           views.doctor_dashboard,  name='doctor_dashboard'),
    path('residents/',                           views.resident_list,     name='doctor_resident_list'),
    path('residents/<int:pk>/',                  views.resident_detail,   name='doctor_resident_detail'),
    path('residents/<int:pk>/add-prescription/', views.add_prescription,  name='doctor_add_prescription'),
    path('residents/<int:pk>/add-lab/',          views.add_lab_report,    name='doctor_add_lab'),
    path('residents/<int:pk>/ai-report/',        views.ai_report,         name='doctor_ai_report'),
]