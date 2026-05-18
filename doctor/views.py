from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from residents.models import ResidentProfile, VitalSign, LabReport, AIHealthReport
from stockkeeper.models import Medicine, Prescription
from accounts.models import CustomUser
import requests


def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'doctor':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@doctor_required
def doctor_dashboard(request):
    # Get residents assigned to this doctor
    my_residents    = ResidentProfile.objects.filter(assigned_doctor=request.user)
    total           = my_residents.count()
    high_risk       = sum(1 for r in my_residents if r.vitals.filter(is_abnormal=True).exists()
                          or r.lab_reports.filter(is_critical=True).exists())
    abnormal_vitals = VitalSign.objects.filter(
        resident__assigned_doctor=request.user, is_abnormal=True).count()
    critical_labs   = LabReport.objects.filter(
        resident__assigned_doctor=request.user, is_critical=True).count()

    recent_vitals = VitalSign.objects.filter(
        resident__assigned_doctor=request.user,
        is_abnormal=True
    ).order_by('-recorded_at')[:5]

    return render(request, 'doctor/dashboard.html', {
        'total':           total,
        'high_risk':       high_risk,
        'abnormal_vitals': abnormal_vitals,
        'critical_labs':   critical_labs,
        'recent_vitals':   recent_vitals,
        'my_residents':    my_residents,
    })


@doctor_required
def resident_list(request):
    query     = request.GET.get('q', '')
    residents = ResidentProfile.objects.filter(assigned_doctor=request.user)
    if query:
        residents = residents.filter(full_name__icontains=query)

    # Build risk data for each resident
    residents_data = []
    for r in residents:
        has_abnormal = r.vitals.filter(is_abnormal=True).exists()
        has_critical = r.lab_reports.filter(is_critical=True).exists()

        if has_abnormal or has_critical:
            risk_level = 'High'
            risk_badge = 'badge-danger'
            risk_icon  = '🔴'
        elif r.vitals.count() == 0:
            risk_level = 'No Data'
            risk_badge = 'badge-warning'
            risk_icon  = '🟡'
        else:
            risk_level = 'Low'
            risk_badge = 'badge-success'
            risk_icon  = '🟢'

        residents_data.append({
            'resident':      r,
            'risk_level':    risk_level,
            'risk_badge':    risk_badge,
            'risk_icon':     risk_icon,
            'vitals_count':  r.vitals.count(),
            'labs_count':    r.lab_reports.count(),
            'abnormal':      r.vitals.filter(is_abnormal=True).count(),
            'critical':      r.lab_reports.filter(is_critical=True).count(),
        })

    return render(request, 'doctor/resident_list.html', {
        'residents_data': residents_data,
        'query':          query,
        'total':          len(residents_data),
    })

@doctor_required
def resident_detail(request, pk):
    resident      = get_object_or_404(ResidentProfile, pk=pk, assigned_doctor=request.user)
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
        risk_reasons.append('All readings within normal range')

    return render(request, 'doctor/resident_detail.html', {
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


@doctor_required
def add_prescription(request, pk):
    resident  = get_object_or_404(ResidentProfile, pk=pk, assigned_doctor=request.user)
    medicines = Medicine.objects.all()
    if request.method == 'POST':
        Prescription.objects.create(
            resident      = resident,
            medicine_id   = request.POST['medicine'],
            dosage        = request.POST['dosage'],
            frequency     = request.POST['frequency'],
            start_date    = request.POST['start_date'],
            end_date      = request.POST.get('end_date') or None,
            prescribed_by = f"Dr. {request.user.username}",
            is_active     = True,
        )
        messages.success(request, 'Prescription added successfully!')
        return redirect('doctor_resident_detail', pk=pk)

    return render(request, 'doctor/add_prescription.html', {
        'resident':  resident,
        'medicines': medicines,
    })


@doctor_required
def add_lab_report(request, pk):
    resident = get_object_or_404(ResidentProfile, pk=pk, assigned_doctor=request.user)
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
        messages.success(request, 'Lab report added!')
        return redirect('doctor_resident_detail', pk=pk)

    return render(request, 'doctor/add_lab_report.html', {'resident': resident})


@doctor_required
def ai_report(request, pk):
    from residents.ai_helper import generate_health_report
    resident    = get_object_or_404(ResidentProfile, pk=pk, assigned_doctor=request.user)
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
            messages.success(request, 'AI report generated!')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('doctor_resident_detail', pk=pk)

    return redirect('doctor_resident_detail', pk=pk)