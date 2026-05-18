from django.urls import path
from . import views

urlpatterns = [
    path('register/',        views.register_view,     name='register'),
    path('login/',           views.login_view,         name='login'),
    path('logout/',          views.logout_view,        name='logout'),
    path('change-password/', views.change_my_password, name='change_my_password'),
    path('forgot-password/', views.forgot_password,    name='forgot_password'),
]