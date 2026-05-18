from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from residents.models import ResidentProfile, VitalSign, LabReport, AIHealthReport
from stockkeeper.models import Medicine, Prescription
from accounts.models import CustomUser
import requests


def caregiver_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'caregiver':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@caregiver_required
def caregiver_dashboard(request):
    total_residents = ResidentProfile.objects.count()
    abnormal_vitals = VitalSign.objects.filter(is_abnormal=True).count()
    critical_labs   = LabReport.objects.filter(is_critical=True).count()
    low_stock       = Medicine.objects.filter(quantity__lt=10).count()
    recent_vitals   = VitalSign.objects.filter(
        is_abnormal=True).order_by('-recorded_at')[:5]

    return render(request, 'caregiver/dashboard.html', {
        'total_residents': total_residents,
        'abnormal_vitals': abnormal_vitals,
        'critical_labs':   critical_labs,
        'low_stock':       low_stock,
        'recent_vitals':   recent_vitals,
    })


@caregiver_required
def resident_list(request):
    query     = request.GET.get('q', '')
    residents = ResidentProfile.objects.all()
    if query:
        residents = residents.filter(full_name__icontains=query)
    return render(request, 'caregiver/resident_list.html', {
        'residents': residents,
        'query':     query,
    })


@caregiver_required
def add_resident(request):
    # ✅ Only ONE add_resident function — with doctors
    doctors = CustomUser.objects.filter(role='doctor')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'caregiver/add_resident.html', {'doctors': doctors})

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            role='resident'
        )

        doctor_id       = request.POST.get('assigned_doctor') or None
        assigned_doctor = None
        if doctor_id:
            try:
                assigned_doctor = CustomUser.objects.get(pk=doctor_id, role='doctor')
            except CustomUser.DoesNotExist:
                assigned_doctor = None

        ResidentProfile.objects.create(
            user               = user,
            full_name          = request.POST['full_name'],
            date_of_birth      = request.POST['date_of_birth'],
            gender             = request.POST['gender'],
            blood_group        = request.POST['blood_group'],
            address            = request.POST['address'],
            emergency_contact  = request.POST['emergency_contact'],
            medical_history    = request.POST.get('medical_history', ''),
            assigned_caregiver = request.user,
            assigned_doctor    = assigned_doctor,
            room_number        = request.POST.get('room_number', ''),
            status             = request.POST.get('status', 'active'),
        )
        messages.success(request, f"Resident added! Username: {username} | Password: {password}")
        return redirect('caregiver_resident_list')

    return render(request, 'caregiver/add_resident.html', {'doctors': doctors})


@caregiver_required
def resident_detail(request, pk):
    resident      = get_object_or_404(ResidentProfile, pk=pk)
    vitals        = resident.vitals.order_by('-recorded_at')[:10]
    lab_reports   = resident.lab_reports.order_by('-uploaded_at')[:10]
    prescriptions = resident.prescriptions.filter(is_active=True)
    latest_ai     = resident.ai_reports.order_by('-generated_at').first()

    risk_level   = 'Low'
    risk_reasons = []
    if resident.vitals.filter(is_abnormal=True).exists():
        risk_level = 'High'
        risk_reasons.append('Abnormal vital signs detected')
    if resident.lab_reports.filter(is_critical=True).exists():
        risk_level = 'High'
        risk_reasons.append('Critical lab results found')
    if not risk_reasons:
        risk_reasons.append('All vitals and lab results within normal range')

    return render(request, 'caregiver/resident_detail.html', {
        'resident':            resident,
        'vitals':              vitals,
        'lab_reports':         lab_reports,
        'prescriptions':       prescriptions,
        'latest_ai':           latest_ai,
        'risk_level':          risk_level,
        'risk_reasons':        risk_reasons,
        'vitals_count':        resident.vitals.count(),
        'prescriptions_count': resident.prescriptions.filter(is_active=True).count(),
        'labs_count':          resident.lab_reports.count(),
        'history_count':       1 if resident.medical_history else 0,
    })


@caregiver_required
def add_vital(request, pk):
    resident = get_object_or_404(ResidentProfile, pk=pk)
    if request.method == 'POST':
        bp     = request.POST['blood_pressure']
        pulse  = int(request.POST['pulse_rate'])
        oxygen = float(request.POST['oxygen_level'])
        temp   = float(request.POST['temperature'])
        sugar  = float(request.POST['blood_sugar'])

        is_abnormal = (
            pulse < 60 or pulse > 100 or
            oxygen < 95 or
            temp > 37.5 or temp < 36 or
            sugar > 140 or sugar < 70
        )

        VitalSign.objects.create(
            resident       = resident,
            blood_pressure = bp,
            pulse_rate     = pulse,
            oxygen_level   = oxygen,
            temperature    = temp,
            blood_sugar    = sugar,
            notes          = request.POST.get('notes', ''),
            is_abnormal    = is_abnormal,
        )
        messages.success(request, 'Vital signs recorded successfully!')
        return redirect('caregiver_resident_detail', pk=pk)

    return render(request, 'caregiver/add_vital.html', {'resident': resident})


@caregiver_required
def add_lab_report(request, pk):
    resident = get_object_or_404(ResidentProfile, pk=pk)
    if request.method == 'POST':
        result_value = float(request.POST['result_value'])
        normal_range = request.POST['normal_range']

        is_critical = False
        try:
            low, high = normal_range.split('-')
            if result_value < float(low) or result_value > float(high):
                is_critical = True
        except:
            is_critical = bool(request.POST.get('is_critical'))

        LabReport.objects.create(
            resident     = resident,
            test_name    = request.POST['test_name'],
            result_value = result_value,
            normal_range = normal_range,
            unit         = request.POST['unit'],
            is_critical  = is_critical,
            pdf_report   = request.FILES.get('pdf_report'),
        )
        messages.success(request, 'Lab report added successfully!')
        return redirect('caregiver_resident_detail', pk=pk)

    return render(request, 'caregiver/add_lab_report.html', {'resident': resident})


@caregiver_required
def add_prescription(request, pk):
    resident  = get_object_or_404(ResidentProfile, pk=pk)
    medicines = Medicine.objects.all()
    if request.method == 'POST':
        Prescription.objects.create(
            resident      = resident,
            medicine_id   = request.POST['medicine'],
            dosage        = request.POST['dosage'],
            frequency     = request.POST['frequency'],
            start_date    = request.POST['start_date'],
            end_date      = request.POST.get('end_date') or None,
            prescribed_by = request.POST['prescribed_by'],
            is_active     = True,
        )
        messages.success(request, 'Prescription added successfully!')
        return redirect('caregiver_resident_detail', pk=pk)

    return render(request, 'caregiver/add_prescription.html', {
        'resident':  resident,
        'medicines': medicines,
    })


@caregiver_required
def assign_doctor(request, pk):
    resident = get_object_or_404(ResidentProfile, pk=pk)
    doctors  = CustomUser.objects.filter(role='doctor')

    if request.method == 'POST':
        doctor_id = request.POST.get('assigned_doctor') or None
        if doctor_id:
            try:
                resident.assigned_doctor = CustomUser.objects.get(pk=doctor_id, role='doctor')
            except CustomUser.DoesNotExist:
                resident.assigned_doctor = None
        else:
            resident.assigned_doctor = None
        resident.save()
        messages.success(request, f'Doctor assigned to {resident.full_name}!')
        return redirect('caregiver_resident_detail', pk=pk)

    return render(request, 'caregiver/assign_doctor.html', {
        'resident': resident,
        'doctors':  doctors,
    })


@caregiver_required
def risk_analysis(request):
    residents = ResidentProfile.objects.all()
    query     = request.GET.get('q', '')

    if query:
        residents = residents.filter(full_name__icontains=query)

    risk_data    = []
    high_count   = 0
    medium_count = 0
    low_count    = 0

    for resident in residents:
        risk_level      = 'Low'
        reasons         = []
        abnormal_vitals = resident.vitals.filter(is_abnormal=True).count()
        critical_labs   = resident.lab_reports.filter(is_critical=True).count()

        if abnormal_vitals > 0:
            risk_level = 'High'
            reasons.append(f'Abnormal vitals ({abnormal_vitals} records)')
        if critical_labs > 0:
            risk_level = 'High'
            reasons.append(f'Critical lab results ({critical_labs} records)')
        if resident.vitals.count() == 0:
            if risk_level == 'Low':
                risk_level = 'Medium'
            reasons.append('No vitals recorded yet')
        if resident.lab_reports.count() == 0:
            reasons.append('No lab reports recorded yet')
        if not reasons:
            reasons.append('All readings within normal range')

        if risk_level == 'High':
            high_count += 1
        elif risk_level == 'Medium':
            medium_count += 1
        else:
            low_count += 1

        risk_data.append({
            'resident':        resident,
            'risk_level':      risk_level,
            'reasons':         reasons,
            'vitals_count':    resident.vitals.count(),
            'labs_count':      resident.lab_reports.count(),
            'abnormal_vitals': abnormal_vitals,
            'critical_labs':   critical_labs,
        })

    order = {'High': 0, 'Medium': 1, 'Low': 2}
    risk_data.sort(key=lambda x: order[x['risk_level']])

    return render(request, 'caregiver/risk_analysis.html', {
        'risk_data':    risk_data,
        'query':        query,
        'high_count':   high_count,
        'medium_count': medium_count,
        'low_count':    low_count,
        'total':        len(risk_data),
    })


@caregiver_required
def ai_report_for_resident(request, pk):
    from residents.ai_helper import generate_health_report
    resident    = get_object_or_404(ResidentProfile, pk=pk)
    vitals      = list(resident.vitals.order_by('-recorded_at')[:5])
    lab_reports = list(resident.lab_reports.order_by('-uploaded_at')[:5])

    if request.method == 'POST':
        try:
            result = generate_health_report(resident, vitals, lab_reports)
            AIHealthReport.objects.create(
                resident   = resident,
                risk_score = result.get('risk_score', 0),
                risk_level = result.get('risk_level', 'Low'),
                summary    = result.get('summary', ''),
                factors    = result.get('factors', ''),
            )
            messages.success(request, 'AI Health Report generated successfully!')
        except Exception as e:
            messages.error(request, f"Could not generate report: {str(e)}")
        return redirect('caregiver_resident_detail', pk=pk)

    return redirect('caregiver_resident_detail', pk=pk)


@caregiver_required
def change_resident_password(request, pk):
    resident = get_object_or_404(ResidentProfile, pk=pk)
    if request.method == 'POST':
        new_password = request.POST['new_password']
        resident.user.set_password(new_password)
        resident.user.save()
        messages.success(
            request,
            f"Password changed! Username: {resident.user.username} | New Password: {new_password}"
        )
        return redirect('caregiver_resident_detail', pk=pk)
    return render(request, 'caregiver/change_password.html', {'resident': resident})