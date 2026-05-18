from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                              views.caregiver_dashboard,      name='caregiver_dashboard'),
    path('residents/',                              views.resident_list,             name='caregiver_resident_list'),
    path('residents/add/',                          views.add_resident,              name='add_resident'),
    path('residents/<int:pk>/',                     views.resident_detail,           name='caregiver_resident_detail'),
    path('residents/<int:pk>/add-vital/',           views.add_vital,                 name='add_vital'),
    path('residents/<int:pk>/add-lab/',             views.add_lab_report,            name='add_lab_report'),
    path('residents/<int:pk>/add-prescription/',    views.add_prescription,          name='add_prescription'),
    path('residents/<int:pk>/assign-doctor/',       views.assign_doctor,             name='assign_doctor'),
    path('residents/<int:pk>/ai-report/',           views.ai_report_for_resident,    name='ai_report_for_resident'),
    path('residents/<int:pk>/change-password/',     views.change_resident_password,  name='change_resident_password'),
    path('risk/',                                   views.risk_analysis,             name='risk_analysis'),
]