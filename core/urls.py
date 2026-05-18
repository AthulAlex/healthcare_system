from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.role == 'caregiver':
            return redirect('caregiver_dashboard')
        elif request.user.role == 'resident':
            return redirect('resident_dashboard')
        elif request.user.role == 'stockkeeper':
            return redirect('stock_dashboard')
        elif request.user.role == 'doctor':
            return redirect('doctor_dashboard')
    return redirect('login')

urlpatterns = [
    # Home — redirect to login or dashboard
    path('', home_redirect, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # Auth pages — accessible directly
    path('login/',           __import__('accounts.views', fromlist=['login_view']).login_view,         name='login'),
    path('register/',        __import__('accounts.views', fromlist=['register_view']).register_view,    name='register'),
    path('logout/',          __import__('accounts.views', fromlist=['logout_view']).logout_view,        name='logout'),
    path('change-password/', __import__('accounts.views', fromlist=['change_my_password']).change_my_password, name='change_my_password'),
    path('forgot-password/', __import__('accounts.views', fromlist=['forgot_password']).forgot_password, name='forgot_password'),

    # App modules
    path('accounts/',     include('accounts.urls')),
    path('residents/',    include('residents.urls')),
    path('caregiver/',    include('caregiver.urls')),
    path('stockkeeper/',  include('stockkeeper.urls')),
    path('doctor/',       include('doctor.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)