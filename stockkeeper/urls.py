from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',              views.stock_dashboard,      name='stock_dashboard'),
    path('medicines/',              views.medicine_list,         name='medicine_list'),
    path('medicines/add/',          views.add_medicine,          name='add_medicine'),
    path('medicines/<int:pk>/update/', views.update_stock,       name='update_stock'),
    path('medicines/<int:pk>/edit/',   views.edit_medicine,      name='edit_medicine'),
    path('medicines/<int:pk>/delete/', views.delete_medicine,    name='delete_medicine'),
    path('export-pdf/',             views.export_inventory_pdf,  name='export_inventory_pdf'),
]