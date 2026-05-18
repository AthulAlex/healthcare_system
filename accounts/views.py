from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role     = request.POST['role']
        phone    = request.POST.get('phone', '').strip()

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = CustomUser.objects.create_user(
            username         = username,
            password         = password,
            role             = role,
            phone            = phone,
            specialization   = request.POST.get('specialization', 'general'),
            department       = request.POST.get('department', 'general_ward'),
            qualification    = request.POST.get('qualification', ''),
            experience_years = int(request.POST.get('experience_years', 0) or 0),
        )
        messages.success(request, 'Account created! Please login.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
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

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user     = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            if user.role == 'caregiver':
                return redirect('caregiver_dashboard')
            elif user.role == 'resident':
                return redirect('resident_dashboard')
            elif user.role == 'stockkeeper':
                return redirect('stock_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('/admin/')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def change_my_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        current  = request.POST['current_password']
        new_pass = request.POST['new_password']
        confirm  = request.POST['confirm_password']

        user = authenticate(request, username=request.user.username, password=current)
        if user is None:
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_my_password')

        if new_pass != confirm:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_my_password')

        if len(new_pass) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('change_my_password')

        request.user.set_password(new_pass)
        request.user.save()
        messages.success(request, 'Password changed! Please login again.')
        return redirect('login')

    return render(request, 'accounts/change_my_password.html')


def forgot_password(request):
    if request.method == 'POST':
        username     = request.POST['username']
        new_password = request.POST['new_password']
        confirm      = request.POST['confirm_password']

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with that username.')
            return redirect('forgot_password')

        if new_password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('forgot_password')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('forgot_password')

        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully! Please login.')
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')